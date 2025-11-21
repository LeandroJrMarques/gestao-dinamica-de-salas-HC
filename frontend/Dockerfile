# Usar Node 20 (LTS) para evitar erros de criptografia do Vite
FROM node:20-alpine

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependência
COPY package*.json ./

# Instalar dependências
RUN npm install

# Copiar o resto dos arquivos
COPY . .

# Expor a porta
EXPOSE 5173

# Comando de inicialização
CMD ["npm", "run", "dev", "--", "--host"]