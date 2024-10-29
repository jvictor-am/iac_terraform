import streamlit as st
from sqlalchemy import create_engine, MetaData, text
import pandas as pd
import psycopg2
import os

# Configurações de conexão com o PostgreSQL no RDS
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_PORT = os.getenv("DB_PORT", "5432")

# Função para criar a conexão com o banco de dados
def init_connection():
    return create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

# Função para criar a tabela de cadastro se não existir
def create_table(engine):
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS pessoas (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            idade INT NOT NULL
        );
        """))
        conn.commit()

# Função para inserir uma nova pessoa
def add_person(engine, nome, email, idade):
    with engine.connect() as conn:
        conn.execute(text(f"INSERT INTO pessoas (nome, email, idade) VALUES ('{nome}', '{email}', {idade})"))
        conn.commit()

# Função para checar o status do banco
def check_db_status(engine):
    with engine.connect() as conn:
        # Obter lista de tabelas e contar o número de linhas de cada tabela
        metadata = MetaData()
        metadata.reflect(bind=engine)
        table_status = []
        for table in metadata.tables.values():
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table.name}"))
            count = result.fetchone()[0]
            table_status.append((table.name, count))
        return table_status

# Interface do Streamlit
st.title('Cadastro de Pessoas')

# Abas
tab1, tab2 = st.tabs(["Formulário de Cadastro", "Status do Banco de Dados"])

# Conexão inicial com o banco de dados
engine = init_connection()
create_table(engine)

# Aba 1: Formulário de cadastro
with tab1:
    st.header("Preencha os dados abaixo:")
    with st.form(key='form_cadastro'):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        idade = st.number_input("Idade", min_value=0, step=1)
        submit_button = st.form_submit_button(label="Cadastrar")

    # Quando o botão de submit é pressionado
    if submit_button:
        if not nome or not email or idade is None:
            st.error("Todos os campos são obrigatórios!")
        else:
            add_person(engine, nome, email, idade)
            st.success(f"Cadastro de {nome} realizado com sucesso!")

# Aba 2: Status do Banco de Dados
with tab2:
    st.header("Status do Banco de Dados")
    status = check_db_status(engine)
    if status:
        for table, count in status:
            st.write(f"Tabela: {table}, Linhas: {count}")
    else:
        st.warning("Nenhuma tabela encontrada no banco de dados.")


# # Transfer the updated web.py to EC2
# scp -i /path/to/your-key-pair.pem web.py ubuntu@<your-ec2-public-ip>:/home/ubuntu/web.py

# # SSH into EC2 instance
# ssh -i /path/to/your-key-pair.pem ubuntu@<your-ec2-public-ip>

# # Kill existing Streamlit process
# pkill -f streamlit

# # Source environment variables
# source /home/ubuntu/.bashrc

# # Start Streamlit application
# nohup /home/ubuntu/venv/bin/streamlit run /home/ubuntu/web.py > /home/ubuntu/streamlit.log 2>&1 &

# # Verify Streamlit process
# ps aux | grep streamlit

# sudo apt update
# sudo apt install postgresql-client -y
# psql -h <rds-endpoint> -d <db-name> -U <db-user> -W
# \dt
# \d pessoas
# SELECT * FROM pessoas;