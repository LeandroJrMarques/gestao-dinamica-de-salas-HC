from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from app.database import engine, Base, get_db
from app.models import Sala, Grade, Alocacao
from app.services.importer import importar_salas_csv, importar_grades_csv
from app.core.optimizer import gerar_alocacao_grade

# Inicializa o Banco de Dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GDS - Gestão Dinâmica de Salas")

# Configuração de CORS
origins = ["http://localhost:5173", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de Entrada
class NovaDemanda(BaseModel):
    medico_nome: str
    especialidade: str
    dia_semana: str
    turno: str
    tipo_recurso: str = "EXTRA"

class CheckInRequest(BaseModel):
    medico_nome: str

@app.get("/")
def read_root():
    return {"message": "API GDS Online", "status": "OK", "mode": "Grade Semanal"}

# Importação dos dados
@app.post("/api/setup/importar-salas")
def trigger_import_salas():
    """Lê o CSV de infraestrutura física e popula o banco"""
    return importar_salas_csv()

@app.post("/api/setup/importar-grades")
def trigger_import_grades():
    """Lê o CSV de grades médicas (AGHU) e popula o banco"""
    return importar_grades_csv()

# Motor de alocação
@app.post("/api/alocacao/gerar")
def trigger_alocacao_inteligente(db: Session = Depends(get_db)):
    """
    Executa o algoritmo que cruza Demanda (Grades) x Oferta (Salas).
    Retorna quem ficou onde e quem ficou sem sala.
    """
    resultado = gerar_alocacao_grade(db)
    
    return {
        "status": "Processamento concluído",
        "total_alocados": len(resultado["alocacoes_detalhadas"]), 
        "total_conflitos": len(resultado["conflitos"]),
        "resumo_executivo": resultado["resumo_ambulatorios"],
        "detalhes": resultado
    }

@app.post("/api/grade/adicionar")
def adicionar_demanda_manual(demanda: NovaDemanda, db: Session = Depends(get_db)):
    """
    Permite ao Gestor adicionar um recurso extra na grade
    (Ex: Um residente que chegou de última hora).
    """
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
    return {"message": "Demanda adicionada à grade com sucesso! Rode a alocação novamente para incluí-lo."}

# Rota para realizar CHECK-IN (Ocupar a sala)
@app.post("/api/salas/{sala_id}/checkin")
def realizar_checkin(sala_id: str, dados: CheckInRequest, db: Session = Depends(get_db)):
    # 1. Busca a sala no banco de dados
    sala = db.query(Sala).filter(Sala.id == sala_id).first()

    if not sala:
        raise HTTPException(status_code = 404, detail="Sala não encontrada")
    
    # 2. Verifica se a sala já está ocupada ou em manutenção
    if sala.status_atual == "OCUPADA":
        raise HTTPException(status_code = 400, detail = f"Sala já ocupada por {sala.ocupante_atual}")
    
    if sala.is_maintenance:
        raise HTTPException(status_code = 400, detail = "Esta sala está em manutenção")

    # 3. Atualizar os status das salas aptas a serem ocupadas
    sala.status_atual = "OCUPADA"
    sala.ocupante_atual = dados.medico_nome
    sala.horario_entrada = datetime.now().strftime("%H:%M") # Pega a hora atual do servidor

    db.commit() # Salva no banco de dados
    db.refresh(sala)

    return {"message": f"Check-in realizado com sucesso para {dados.medico_nome}", "sala": sala}

# Rota para realizar CHECK-OUT(desocupar sala)
@app.post("/api/salas/{sala_id}/checkout")  
def realizar_checkout(sala_id: str, db: Session = Depends(get_db)):
    sala = db.query(Sala).filter(Sala.id == sala_id).first()

    if not sala:
        raise HTTPException(status_code=404, detail="Sala não encontrada")
        
    if sala.status_atual == "LIVRE":
        return {"message": "Sala já está livre"}

    # Lógica de liberar sala
    medico_anterior = sala.ocupante_atual
    sala.status_atual = "LIVRE"
    sala.ocupante_atual = None
    sala.horario_entrada = None

    db.commit()

    return {"message": f"Check-out realizado. Sala liberada por {medico_anterior}."}  

# Visualização dos dados
@app.get("/api/salas")
def listar_salas(db: Session = Depends(get_db)):
    return db.query(Sala).all()

@app.get("/api/salas/ociosas")
def listar_salas_ociosas(db: Session = Depends(get_db)):
    # Retorna apenas as salas que estão LIVRES no momento, ignorando se existia agendamento prévio ou não. Isso resolve o problema da ociosidade
    salas_livres = db.query(Sala).filter(
        Sala.status_atual == "LIVRE",
        Sala.is_maintenance == False
    ).all()

    return {
        "total_livres": len(salas_livres),
        "salas": salas_livres
    }
    # Se o médico agendado chegar e encontrar alguém na sala que ele deveria ocupar, ele vai encontrar a mensagem de erro:
    # Sala ocupada por {residente}. Dessa forma, ele deverá ocupar outra sala utilizando o listar_salas_ociosas

@app.get("/api/grades")
def listar_demanda(db: Session = Depends(get_db)):
    return db.query(Grade).all()

@app.get("/api/alocacoes")
def listar_alocacoes_finais(db: Session = Depends(get_db)):
    """Retorna a grade final montada (Sala + Médico + Horário)"""
    alocacoes = db.query(Alocacao).all()
    return alocacoes