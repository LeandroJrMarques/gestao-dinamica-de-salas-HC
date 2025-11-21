# Imagem base
FROM python:3.11-slim

# Define pasta de trabalho dentro do container
WORKDIR /app

# Copia e instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código todo
COPY . .

# Comando para rodar o servidor (Hot-reload ativado)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]