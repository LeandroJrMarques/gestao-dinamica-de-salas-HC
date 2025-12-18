from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from collections import defaultdict

from app.database import engine, Base, SessionLocal
from app.models import Sala, Grade, Alocacao
from app.services.importer import importar_salas_csv, importar_grades_csv
from app.core.optimizer import (
    gerar_alocacao_grade, 
    calcular_afinidade_tempo_real, 
    descobrir_andar_predominante, 
    obter_resumo_atual
)
from app.core.time import sincronizar_status_com_alocacao

# Inicializa o Banco
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GDS - Gestão Dinâmica de Salas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelos
class NovaDemanda(BaseModel):
    medico_nome: str
    especialidade: str
    dia_semana: str
    turno: str
    tipo_recurso: str = "EXTRA"

class CheckInRequest(BaseModel):
    medico_nome: str

class AutoCheckInRequest(BaseModel):
    medico_nome: str
    especialidade: str

@app.get("/")
def read_root():
    return {"message": "API GDS Online", "status": "OK", "mode": "Grade Semanal"}

@app.post("/api/setup/importar-salas")
def trigger_import_salas():
    return importar_salas_csv()

@app.post("/api/setup/importar-grades")
def trigger_import_grades():
    return importar_grades_csv()

@app.post("/api/alocacao/gerar")
def trigger_alocacao_inteligente(teste_dia: str = None, teste_turno: str = None, db: Session = Depends(get_db)):
    # Gera
    resultado = gerar_alocacao_grade(db)
    
    # Simula status de tempo real
    try:
        qtd_ocupadas, dia_usado, turno_usado = sincronizar_status_com_alocacao(db, forcar_dia=teste_dia, forcar_turno=teste_turno)
    except:
        qtd_ocupadas = 0
        dia_usado = "N/A"
        turno_usado = "N/A"

    resultado["modo"] = "TESTE MANUAL" if teste_dia else "TEMPO REAL AUTOMÁTICO"
    resultado["contexto_usado"] = f"{dia_usado} - {turno_usado}"
    resultado["salas_ocupadas_agora"] = qtd_ocupadas
    
    return resultado

@app.post("/api/grade/adicionar")
def adicionar_demanda_manual(demanda: NovaDemanda, db: Session = Depends(get_db)):
    nova_grade = Grade(
        nome_profissional=demanda.medico_nome,
        especialidade=demanda.especialidade,
        dia_semana=demanda.dia_semana,
        turno=demanda.turno,
        tipo_recurso=demanda.tipo_recurso,
        origem="GESTOR"
    )
    db.add(nova_grade)
    db.commit()
    return {"message": "Demanda adicionada."}

@app.post("/api/salas/{sala_id}/checkin")
def realizar_checkin(sala_id: str, dados: CheckInRequest, db: Session = Depends(get_db)):
    sala = db.query(Sala).filter(Sala.id == sala_id).first()
    if not sala: raise HTTPException(status_code = 404, detail="Sala não encontrada")
    
    sala.status_atual = "OCUPADA"
    sala.ocupante_atual = dados.medico_nome
    sala.horario_entrada = datetime.now().strftime("%H:%M") 
    db.commit()
    return {"message": f"Check-in realizado para {dados.medico_nome}", "sala": sala}

@app.post("/api/salas/checkin/inteligente")
def checkin_semiautomatico(dados: AutoCheckInRequest, db: Session = Depends(get_db)):
    andar_predominante, num_ideal = descobrir_andar_predominante(db, dados.especialidade)
    salas_disponiveis = db.query(Sala).filter(Sala.status_atual == "LIVRE", Sala.is_maintenance == False).all()
    if not salas_disponiveis: raise HTTPException(status_code=404, detail="Não há nenhuma sala livre.")
    
    melhor_sala = None
    maior_score = -999
    for sala in salas_disponiveis:
        score = calcular_afinidade_tempo_real(sala, dados.especialidade, andar_predominante, num_ideal)
        if score > maior_score:
            maior_score = score
            melhor_sala = sala
            
    if not melhor_sala: melhor_sala = salas_disponiveis[0]

    melhor_sala.status_atual = "OCUPADA"
    melhor_sala.ocupante_atual = dados.medico_nome
    melhor_sala.horario_entrada = datetime.now().strftime("%H:%M")
    db.commit()
    return {"mensagem": "Check-in realizado", "sala_alocada": melhor_sala}

@app.post("/api/salas/{sala_id}/checkout")  
def realizar_checkout(sala_id: str, db: Session = Depends(get_db)):
    sala = db.query(Sala).filter(Sala.id == sala_id).first()
    if not sala: raise HTTPException(status_code=404, detail="Sala não encontrada")
    sala.status_atual = "LIVRE"
    sala.ocupante_atual = None
    sala.horario_entrada = None
    db.commit()
    return {"message": "Check-out realizado."}

@app.get("/api/salas")
def listar_salas(db: Session = Depends(get_db)):
    return db.query(Sala).all()

@app.get("/api/salas/ociosas")
def listar_salas_ociosas(db: Session = Depends(get_db)):
    salas_livres = db.query(Sala).filter(Sala.status_atual == "LIVRE", Sala.is_maintenance == False).all()
    return {"total_livres": len(salas_livres), "salas": salas_livres}

@app.get("/api/grades")
def listar_demanda(db: Session = Depends(get_db)):
    return db.query(Grade).all()

@app.get("/api/alocacoes")
def listar_alocacoes_finais(db: Session = Depends(get_db)):
    return db.query(Alocacao).all()

@app.get("/api/mapa-especialidades")
def listar_especialidades_das_salas(db: Session = Depends(get_db)):
    dados = db.query(Sala.id, Sala.especialidade_preferencial).all()
    mapa = defaultdict(list)
    for sala_id, especialidade in dados:
        chave = especialidade.strip() if especialidade and especialidade.strip() else "SEM_PREFERENCIA"
        mapa[chave].append(sala_id)
    return dict(sorted(mapa.items()))

@app.get("/api/alocacao/resumo")
def ler_alocacao_existente(db: Session = Depends(get_db)):
    # Se vazio, gera. Se não, apenas lê.
    if db.query(Alocacao).count() == 0:
        return trigger_alocacao_inteligente(db=db)
    
    resultado = obter_resumo_atual(db)
    
    try:
        qtd_ocupadas, dia_usado, turno_usado = sincronizar_status_com_alocacao(db)
    except:
        qtd_ocupadas, dia_usado, turno_usado = (0, "N/A", "N/A")
        
    resultado["modo"] = "PERSISTIDO"
    resultado["contexto_usado"] = f"{dia_usado} - {turno_usado}"
    resultado["salas_ocupadas_agora"] = qtd_ocupadas
    return resultado