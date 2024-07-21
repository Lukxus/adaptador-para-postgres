# adaptador-para-postgres
Projeto com objetivo de traduzir para uma estrutura SQL, os inserts necessários atraves da leitura e tranformação de dados no formato csv

Modelo de dominio do banco

![alt text](<Blank diagram - Page 1 (4).png>)

![Blank diagram - Page 1](https://github.com/user-attachments/assets/b3a8d17b-1d82-49ca-b4fc-0a82c9b21efa)


# Como subir um banco postgres localmente

1. Baixar a versão: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
2. Setar configs da instalação


# Estrutura

project/
│
├── main.py
├── config.py
├── database.py
├── dataprocessor.py
├── inserter.py
└── .env

- **main.py**: Script principal que executa a inserção dos dados.
- **config.py**: Carrega as configurações do banco de dados a partir do arquivo `.env`.
- **database.py**: Contém a classe `Database` que gerencia a conexão com o banco de dados.
- **dataprocessor.py**: Contém a classe `DataProcessor` que processa os dados.
- **inserter.py**: Contém a classe `Inserter` que executa as operações de inserção no banco de dados.
- **.env**: Arquivo que contém as variáveis de ambiente, como configurações do banco de dados.

# Como gerar os requirements:
pip freeze > requirements.txt


# Requisitos

- Python 3.6 ou superior
- PostgreSQL

# Configuração

## Passo 1: Clonar o repositório
## Passo 2: baixar as bibliotecas necessárias
pip install -r requirements.txt
## Passo 3: Configurar .env
DB_HOST=localhost
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
# Passo 4: Executar Script_Inicial.sql
# Passo 5: Executar main.py




