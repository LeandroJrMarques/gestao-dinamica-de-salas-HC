# GDS - Gestão Dinâmica de Salas (HC-UFPE)

**Prova de Conceito (POC)** para otimização da alocação de consultórios ambulatoriais no Hospital das Clínicas da UFPE.
Projeto de extensão integrado à disciplina de Integração e Evolução de Sistemas de Informação.

---

## 🎯 O Problema vs. A Solução

Atualmente, a alocação das salas ambulatoriais é feita manualmente através de planilhas estáticas. Isso gera ineficiência, dificuldade em lidar com absenteísmo de pacientes e falta de visibilidade em tempo real sobre salas ociosas.

**A Solução (GDS):** Uma plataforma digital que substitui a planilha por um sistema vivo.
    1.  **Planejamento Inteligente:** Importa a demanda do AGHU e sugere a alocação ideal.
    2.  **Gestão em Tempo Real:** Um portal para médicos e residentes realizarem "check-in/check-out", atualizando um Dashboard de ocupação visível para todos.

---

## 🛠️ Tech Stack

O projeto utiliza uma arquitetura moderna baseada em microsserviços e conteinerização, seguindo o padrão de desenvolvimento do HC.

### **Backend**
* **Linguagem:** Python 3.11
* **Framework:** FastAPI (Alta performance e documentação automática)
* **Validação de Dados:** Pydantic
* **Servidor:** Uvicorn

### **Frontend**
* **Framework:** Vue 3 (Composition API)
* **Linguagem:** TypeScript
* **Build Tool:** Vite
* **Estilização:** Tailwind CSS (v4)

### **Infraestrutura**
* **Docker & Docker Compose:** Orquestração de todo o ambiente de desenvolvimento.

---

## 🚀 Como Rodar o Projeto

Siga os passos abaixo para levantar o ambiente completo (Frontend + Backend) em poucos minutos.

### Pré-requisitos
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e rodando.
* Git instalado.

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd gestao-dinamica-de-salas-hc
    ```

2.  **Suba os containers:**
    Na raiz do projeto, execute:
    ```bash
    docker-compose up --build
    ```

3.  **Acesse a Aplicação:**

    * **Frontend (Aplicação Web):** [http://localhost:5173](http://localhost:5173)
    * **Backend (Documentação API / Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📂 Estrutura do Projeto

O repositório está organizado como um Monorepo:

```text
/
├── docker-compose.yml    # Orquestração dos serviços (Back + Front)
├── backend/              # API Python/FastAPI
│   ├── app/
│   │   ├── main.py       # Entrypoint da API
│   │   ├── models.py     # Modelos de Dados (Pydantic)
│   │   └── core/         # Lógica de Negócio e Algoritmo de Alocação
│   ├── requirements.txt  # Dependências Python
│   └── Dockerfile        # Configuração da imagem Backend
│
└── frontend/             # Aplicação Vue 3
    ├── src/
    │   ├── components/   # Componentes reutilizáveis (ex: RoomCard)
    │   ├── views/        # Telas (Dashboard, Login, Portal)
    │   └── style.css     # Configuração do Tailwind v4
    ├── package.json      # Dependências Node
    └── Dockerfile        # Configuração da imagem Frontend
```