from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GDS - Gestão Dinâmica de Salas")

# Configuração de CORS (Permite que o Front fale com o Back)
origins = [
    "http://localhost:5173",  # Porta padrão do Vite
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API GDS Online", "status": "OK"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}