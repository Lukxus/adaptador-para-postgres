import pandas as pd
import psycopg2
from psycopg2 import sql
import logging
import ast
from datetime import datetime
import re

# Configurações do banco de dados
DB_HOST = 'vlr.c56wu8yaivfb.us-east-2.rds.amazonaws.com'
DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

# Configuração de logging
logging.basicConfig(filename='db_inserts.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')

# Função para conectar ao banco de dados
def connect_db():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# Função para executar comandos SQL em lotes com transações
def execute_sql_in_batches(conn, inserts, batch_size):
    with conn.cursor() as cursor:
        for i in range(0, len(inserts), batch_size):
            batch_inserts = inserts[i:i + batch_size]
            try:
                cursor.execute("BEGIN;")
                for insert in batch_inserts:
                    cursor.execute(insert[0], insert[1])
                cursor.execute("COMMIT;")
                logging.info(f"Batch {i // batch_size + 1} executed successfully.")
            except Exception as e:
                cursor.execute("ROLLBACK;")
                logging.error(f"Error executing batch {i // batch_size + 1}: {str(e)}")
                raise



# Carregar o arquivo CSV
file_path = r'D:\\Documents\\vlrcorte\\dados.csv'
df = pd.read_csv(file_path)

# Função para gerar script de insert para a tabela Campeonatos
def generate_campeonatos_insert(df):
    campeonatos = df['campeonato'].apply(lambda x: eval(x)[0]).unique()
    insert_statements = []
    for campeonato in campeonatos:
        insert_statements.append(("INSERT INTO Campeonatos (Nome) VALUES (%s);", (truncate_value(campeonato),)))
    return insert_statements

# Função para gerar script de insert para a tabela Times
def generate_times_insert(df):
    times = pd.concat([df['nomePrimeiroTime'], df['nomeSegundoTime']]).unique()
    insert_statements = []
    for time in times:
        insert_statements.append(("INSERT INTO Times (Nome) VALUES (%s);", (truncate_value(time),)))
    return insert_statements

# Função para gerar script de insert para a tabela Mapa
def generate_mapa_insert(df):
    mapas = df['mapas'].apply(lambda x: eval(x)).explode().unique()
    insert_statements = []
    for mapa in mapas:
        if mapa != 'N/A':
            insert_statements.append(("INSERT INTO Mapa (Nome) VALUES (%s);", (truncate_value(mapa),)))
    return insert_statements

# Função para gerar script de insert para a tabela Sequencia_Partida
def generate_sequencia_partida_insert(df):
    insert_statements = []
    for index, row in df.iterrows():
        campeonato = eval(row['campeonato'])[0]
        insert_statements.append((
            "INSERT INTO Sequencia_Partida (Campeonato, Data, Patch, Tipo, ID_time1, ID_time2) VALUES "
            "((SELECT ID FROM Campeonatos WHERE Nome = %s), %s, %s, %s, (SELECT ID FROM Times WHERE Nome = %s), (SELECT ID FROM Times WHERE Nome = %s));",
            (truncate_value(campeonato), row['date'], truncate_value(row['patch']), truncate_value(row['tipo_partida']), row['nomePrimeiroTime'], row['nomeSegundoTime'])
        ))
    return insert_statements

# Função para gerar script de insert para a tabela Partida
def generate_partida_insert(df):
    insert_statements = []
    for index, row in df.iterrows():
        mapas = eval(row['mapas'])
        for mapa in mapas:
            if mapa != 'N/A':
                insert_statements.append((
                    "INSERT INTO Partida (ID_sequencia_partida, Mapa) VALUES "
                    "((SELECT ID FROM Sequencia_Partida WHERE Data = %s AND Patch = %s AND ID_time1 = (SELECT ID FROM Times WHERE Nome = %s)), (SELECT ID FROM Mapa WHERE Nome = %s));",
                    (row['date'], truncate_value(row['patch']), row['nomePrimeiroTime'], truncate_value(mapa))
                ))
    return insert_statements

# Função para gerar script de insert para a tabela Rounds_Partida
def generate_rounds_partida_insert(df):
    insert_statements = []
    for index, row in df.iterrows():
        rounds = eval(row['rounds'])
        mapas = eval(row['mapas'])
        for mapa, round_data in zip(mapas, rounds):
            if mapa != 'N/A':
                for result in round_data:
                    insert_statements.append((
                        "INSERT INTO Rounds_Partida (ID_partida, Lista_de_resultados) VALUES "
                        "((SELECT ID FROM Partida WHERE ID_sequencia_partida = (SELECT ID FROM Sequencia_Partida WHERE Data = %s AND Patch = %s AND ID_time1 = (SELECT ID FROM Times WHERE Nome = %s))), %s);",
                        (row['date'], truncate_value(row['patch']), row['nomePrimeiroTime'], result)
                    ))
    return insert_statements

# Função para gerar script de insert para a tabela Jogadores
def generate_jogadores_insert(df):
    insert_statements = []
    jogadores = []
    for index, row in df.iterrows():
        estatisticas = eval(row['estatisticas'])
        for partida in estatisticas:
            for jogador in partida:
                jogador_nome = truncate_value(jogador['name'])
                time_nome = truncate_value(row['nomePrimeiroTime']) if jogador_nome not in jogadores else truncate_value(row['nomeSegundoTime'])
                jogadores.append(jogador_nome)
                insert_statements.append((
                    "INSERT INTO Jogadores (Nome, ID_time) VALUES (%s, (SELECT ID FROM Times WHERE Nome = %s));",
                    (jogador_nome, time_nome)
                ))
    return insert_statements

# Função para gerar script de insert para a tabela Partida_Jogador
def generate_partida_jogador_insert(df):
    insert_statements = []
    for index, row in df.iterrows():
        estatisticas = eval(row['estatisticas'])
        for partida in estatisticas:
            for jogador in partida:
                kda_defesa = jogador.get('kda', {}).get('defesa', None)
                kda_ataque = jogador.get('kda', {}).get('ataque', None)
                kda_geral = jogador.get('kda', {}).get('geral', None)

                kast_defesa = jogador.get('kast', {}).get('defesa', None)
                kast_ataque = jogador.get('kast', {}).get('ataque', None)
                kast_geral = jogador.get('kast', {}).get('geral', None)

                adr_defesa = jogador.get('adr', {}).get('defesa', None)
                adr_ataque = jogador.get('adr', {}).get('ataque', None)
                adr_geral = jogador.get('adr', {}).get('geral', None)

                hs_defesa = jogador.get('hs%', {}).get('defesa', None)
                hs_ataque = jogador.get('hs%', {}).get('ataque', None)
                hs_geral = jogador.get('hs%', {}).get('geral', None)

                fk_defesa = jogador.get('fk', {}).get('defesa', None)
                fk_ataque = jogador.get('fk', {}).get('ataque', None)
                fk_geral = jogador.get('fk', {}).get('geral', None)

                fd_defesa = jogador.get('fd', {}).get('defesa', None)
                fd_ataque = jogador.get('fd', {}).get('ataque', None)
                fd_geral = jogador.get('fd', {}).get('geral', None)

                fkfd_defesa = jogador.get('fkfd', {}).get('defesa', None)
                fkfd_ataque = jogador.get('fkfd', {}).get('ataque', None)
                fkfd_geral = jogador.get('fkfd', {}).get('geral', None)

                insert_statements.append((
                    "INSERT INTO Partida_Jogador (ID_jogador, ID_partida, ID_agente, R_defesa, R_ataque, R_geral, ACS_defesa, ACS_ataque, ACS_geral, "
                    "K_defesa, K_ataque, K_geral, D_defesa, D_ataque, D_geral, A_defesa, A_ataque, A_geral, KDA_defesa, KDA_ataque, KDA_geral, KAST_defesa, "
                    "KAST_ataque, KAST_geral, ADR_defesa, ADR_ataque, ADR_geral, HS_defesa, HS_ataque, HS_geral, FK_defesa, FK_ataque, FK_geral, FD_defesa, "
                    "FD_ataque, FD_geral, FKFD_defesa, FKFD_ataque, FKFD_geral) VALUES "
                    "((SELECT ID FROM Jogadores WHERE Nome = %s), "
                    "(SELECT ID FROM Partida WHERE ID_sequencia_partida = (SELECT ID FROM Sequencia_Partida WHERE Data = %s AND Patch = %s AND ID_time1 = "
                    "(SELECT ID FROM Times WHERE Nome = %s))), (SELECT ID FROM Agente WHERE Nome = %s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                    "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                    (
                        truncate_value(jogador['name']), row['date'], truncate_value(row['patch']), row['nomePrimeiroTime'],
                        truncate_value(jogador['agente']), jogador['r']['defesa'], jogador['r']['ataque'], jogador['r']['geral'],
                        jogador['acs']['defesa'], jogador['acs']['ataque'], jogador['acs']['geral'],
                        jogador['k']['defesa'], jogador['k']['ataque'], jogador['k']['geral'],
                        jogador['d']['defesa'], jogador['d']['ataque'], jogador['d']['geral'],
                        jogador['a']['defesa'], jogador['a']['ataque'], jogador['a']['geral'],
                        kda_defesa, kda_ataque, kda_geral, kast_defesa, kast_ataque, kast_geral,
                        adr_defesa, adr_ataque, adr_geral, hs_defesa, hs_ataque, hs_geral,
                        fk_defesa, fk_ataque, fk_geral, fd_defesa, fd_ataque, fd_geral,
                        fkfd_defesa, fkfd_ataque, fkfd_geral
                    )
                ))
    return insert_statements



# Função para truncar valores de texto
def truncate_value(value, max_length=255):
    if isinstance(value, str) and len(value) > max_length:
        return value[:max_length]
    return value

def extract_patch_info(text):
    match = re.search(r'Patch (\d+(\.\d+)?)', text)
    if match:
        return match.group(0)  
    else:
        return None


"""
DO UPDATE SET Nome = EXCLUDED.Nome:

Quando ocorre um conflito, em vez de lançar um erro, o PostgreSQL executa uma atualização no registro existente.
EXCLUDED.Nome refere-se ao valor do Nome que foi fornecido na tentativa de inserção e que causou o conflito.
No contexto específico DO UPDATE SET Nome = EXCLUDED.Nome, a ação de atualização está configurada para não fazer 
nada efetivamente (atualizando Nome com o mesmo valor), mas essa cláusula é necessária para permitir a continuação da operação sem erro.
Essa abordagem serve para ativar a cláusula RETURNING, mesmo quando ocorre um conflito.
"""

def geraScript(dataframe):
    insert_statements = []
    for index, row in dataframe.iterrows():
        campeonato_completo = ast.literal_eval(row["campeonato"])
        insert_statements.append((
            "INSERT INTO Campeonatos (Nome, Especificacao) VALUES (%s, %s) "
            "ON CONFLICT (Nome, Especificacao) DO UPDATE SET Nome = EXCLUDED.Nome "
            "RETURNING ID;", 
            (campeonato_completo[0], campeonato_completo[1])
        ))
    
    return insert_statements


all_inserts = geraScript(df)

conn = connect_db()
try:
    execute_sql_in_batches(conn, all_inserts, 1000)
finally:
    conn.close()
