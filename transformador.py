import pandas as pd
import psycopg2
from psycopg2 import sql
import logging
import ast
from datetime import datetime
import re

# Configurações do banco de dados
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

# Configuração de logging
logging.basicConfig(
    filename="db_inserts.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
)


# Função para conectar ao banco de dados
def connect_db():
    try:
        logging.info("Connecting to the database...")
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            options="-c client_encoding=UTF8",  # Definindo codificação UTF-8
        )
        logging.info("Connection successful.")
        return conn
    except psycopg2.Error as e:
        logging.error(f"Error connecting to the database: {e}")
        raise


# Função para executar comandos SQL em lotes com transações
def execute_sql_in_batches(conn, inserts, batch_size):
    with conn.cursor() as cursor:
        for i in range(0, len(inserts), batch_size):
            batch_inserts = inserts[i : i + batch_size]
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
file_path = r"D:\\Documents\\vlrcorte\\dados.csv"
df = pd.read_csv(file_path)


def extract_patch_info(text):
    # Expressão regular para capturar a palavra "Patch" seguida por um número com qualquer quantidade de dígitos antes e depois do ponto decimal
    match = re.search(r"Patch (\d+(\.\d+)?)", text)
    if match:
        return match.group(0)  # Retorna a correspondência inteira "Patch X.X"
    else:
        return None


def insereCampeonato(conn, campeonatoLista):
    id_campeonato = ""
    query = (
        "INSERT INTO Campeonatos (Nome, Especificacao) VALUES (%s, %s) "
        "ON CONFLICT (Nome, Especificacao) DO UPDATE SET Nome = EXCLUDED.Nome "
        "RETURNING ID;",
        (campeonatoLista[0], campeonatoLista[1]),
    )
    with conn.cursor() as cursor:
        try:
            cursor.execute("BEGIN;")
            cursor.execute(query[0], query[1])
            result = cursor.fetchone()
            cursor.execute("COMMIT;")
            if result:
                id_campeonato = result[0]

        except Exception as e:
            cursor.execute("ROLLBACK;")
            logging.error(
                f"Error executing campeonato insert: {(campeonatoLista[0], campeonatoLista[1])} : {str(e)}"
            )
            raise
    return id_campeonato


insert_statements = []


def transformaRounds(rounds):
    lista = ast.literal_eval(rounds)
    # print(dicionario)
    return lista


"""
EQUIPE1DESARMA = 1
EQUIPE1DETONA = 2
EQUIPE1ELIMINA = 3
EQUIPE1TEMPO = 4
EQUIPE2DESARMA = 5
EQUIPE2DETONA = 6
EQUIPE2ELIMINA = 7
EQUIPE2TEMPO = 8
"""


def criaLabelVencedor(rounds_lista):
    timeUm = 0
    timeDois = 0
    for round in rounds_lista:
        if round <= 4:
            timeUm += 1
        else:
            timeDois += 1
    # print(f"Time 1: {timeUm}")
    # print(f"Time 2: {timeDois}")
    if timeUm > timeDois:
        return "TIME1"
    else:
        return "TIME2"


def insereTimes(conn, time):
    id_campeonato = ""
    query = (
        "INSERT INTO Times (Nome) VALUES (%s) "
        "ON CONFLICT (Nome) DO UPDATE SET Nome = EXCLUDED.Nome "
        "RETURNING ID;",
        (time,),
    )
    with conn.cursor() as cursor:
        try:
            cursor.execute("BEGIN;")
            cursor.execute(query[0], query[1])
            result = cursor.fetchone()
            cursor.execute("COMMIT;")
            if result:
                id_campeonato = result[0]

        except Exception as e:
            cursor.execute("ROLLBACK;")
            logging.error(f"Error executing time insert: {(time)} : {str(e)}")
            raise
    return id_campeonato


def insereSequenciaPartidas(
    conn, campeonato, data, patch, tipo, id_time1, id_time2, url
):
    id_sequencia_partida = None
    query = (
        "INSERT INTO Sequencia_Partida (Campeonato, Data, Patch, Tipo, ID_time1, ID_time2, URL) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s) "
        "RETURNING ID;",
        (campeonato, data, patch, tipo, id_time1, id_time2, url),
    )
    with conn.cursor() as cursor:
        try:
            cursor.execute("BEGIN;")
            cursor.execute(query[0], query[1])
            result = cursor.fetchone()
            cursor.execute("COMMIT;")
            if result:
                id_sequencia_partida = result[0]

        except Exception as e:
            cursor.execute("ROLLBACK;")
            logging.error(
                f"Error executing sequencia_partida insert: {(campeonato, data, patch, tipo, id_time1, id_time2, url)} : {str(e)}"
            )
            raise
    return id_sequencia_partida


def inserePartida(conn, id_sequencia_partida, mapa, id_time_vencedor):
    id_partida = None
    query = (
        "INSERT INTO Partida (ID_sequencia_partida, Mapa, ID_time_vencedor) "
        "VALUES (%s, %s, %s) "
        "RETURNING ID;",
        (id_sequencia_partida, mapa, id_time_vencedor),
    )
    with conn.cursor() as cursor:
        try:
            cursor.execute("BEGIN;")
            cursor.execute(query[0], query[1])
            result = cursor.fetchone()
            cursor.execute("COMMIT;")
            if result:
                id_partida = result[0]

        except Exception as e:
            cursor.execute("ROLLBACK;")
            logging.error(
                f"Error executing partida insert: {(id_sequencia_partida, mapa, id_time_vencedor)} : {str(e)}"
            )
            raise
    return id_partida


def transformaRounds(rounds):
    lista = ast.literal_eval(rounds)
    # print(dicionario)
    return lista


def trataEstatisiticas(estatisticas):
    dicionario = ast.literal_eval(estatisticas)
    # print(dicionario)
    return dicionario


def insereRoundsPartida(conn, id_partida, lista_de_resultados):
    id_round_partida = None
    query = (
        "INSERT INTO Rounds_Partida (ID_partida, Lista_de_resultados) "
        "VALUES (%s, %s) "
        "RETURNING ID;",
        (id_partida, lista_de_resultados),
    )
    with conn.cursor() as cursor:
        try:
            cursor.execute("BEGIN;")
            cursor.execute(query[0], query[1])
            result = cursor.fetchone()
            cursor.execute("COMMIT;")
            if result:
                id_round_partida = result[0]

        except Exception as e:
            cursor.execute("ROLLBACK;")
            logging.error(
                f"Error executing rounds_partida insert: {(id_partida, lista_de_resultados)} : {str(e)}"
            )
            raise
    return id_round_partida


def insereJogador(conn, nome, id_time):
    id_jogador = None
    insert_query = (
        "INSERT INTO Jogadores (Nome, ID_time) "
        "VALUES (%s, %s) "
        "ON CONFLICT (Nome, ID_time) DO NOTHING "
        "RETURNING ID;",
        (nome, id_time),
    )
    select_query = (
        "SELECT ID FROM Jogadores WHERE Nome = %s AND ID_time = %s;",
        (nome, id_time),
    )
    with conn.cursor() as cursor:
        try:
            cursor.execute("BEGIN;")
            cursor.execute(insert_query[0], insert_query[1])
            result = cursor.fetchone()
            if result:
                id_jogador = result[0]
            else:
                cursor.execute(select_query[0], select_query[1])
                result = cursor.fetchone()
                if result:
                    id_jogador = result[0]
            cursor.execute("COMMIT;")

        except Exception as e:
            cursor.execute("ROLLBACK;")
            logging.error(
                f"Error executing jogador insert: {(nome, id_time)} : {str(e)}"
            )
            raise
    return id_jogador


def removeTimeDoNome(name):
    if name:
        ultimo_espaco = name.rfind(" ")
        if ultimo_espaco != -1:
            return name[:ultimo_espaco]
        else:
            return name

def inserePartidaJogador(conn, id_partida, id_jogador, agente, estatisticas):
    id_partida_jogador = None
    
    # Função para tratar valores que podem ser None ou strings vazias
    def safe_get_int(dictionary, key, default=-999):
        value = dictionary.get(key, default)
        if value in [None, '']:
            return default
        return int(value)
    
    def safe_get_float(dictionary, key, default=-999.0):
        value = dictionary.get(key, default)
        if value in [None, '']:
            return default
        return float(value)
    
    def safe_get_simbol(dictionary, key, default=-999.0):
        value = dictionary.get(key, default)
        if value in [None, '']:
            return default
        elif value in ["+", "-"]:
            return int(value)
        elif value in ['%']:
            return int(value[:-1])
        return value
    
    

    query = (
        "INSERT INTO Partida_Jogador (ID_partida, ID_jogador, agente, R_defesa, R_ataque, R_geral, ACS_defesa, ACS_ataque, ACS_geral, "
        "K_defesa, K_ataque, K_geral, D_defesa, D_ataque, D_geral, A_defesa, A_ataque, A_geral, KDA_defesa, KDA_ataque, KDA_geral, "
        "KAST_defesa, KAST_ataque, KAST_geral, ADR_defesa, ADR_ataque, ADR_geral, HS_defesa, HS_ataque, HS_geral, FK_defesa, FK_ataque, "
        "FK_geral, FD_defesa, FD_ataque, FD_geral, FKFD_defesa, FKFD_ataque, FKFD_geral) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
        "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        "RETURNING ID;",
        (
            id_partida, id_jogador, agente,
            safe_get_float(estatisticas["r"], "defesa"), safe_get_float(estatisticas["r"], "ataque"), safe_get_float(estatisticas["r"], "geral"),
            safe_get_int(estatisticas["acs"], "defesa"), safe_get_int(estatisticas["acs"], "ataque"), safe_get_int(estatisticas["acs"], "geral"),
            safe_get_int(estatisticas["k"], "defesa"), safe_get_int(estatisticas["k"], "ataque"), safe_get_int(estatisticas["k"], "geral"),
            safe_get_int(estatisticas["d"], "defesa"), safe_get_int(estatisticas["d"], "ataque"), safe_get_int(estatisticas["d"], "geral"),
            safe_get_int(estatisticas["a"], "defesa"), safe_get_int(estatisticas["a"], "ataque"), safe_get_int(estatisticas["a"], "geral"),
            safe_get_simbol(estatisticas["kda+-"], "defesa"), safe_get_simbol(estatisticas["kda+-"], "ataque"), safe_get_simbol(estatisticas["kda+-"], "geral"),
            safe_get_simbol(estatisticas["kast"], "defesa"), safe_get_simbol(estatisticas["kast"], "ataque"), safe_get_simbol(estatisticas["kast"], "geral"),
            safe_get_int(estatisticas["adr"], "defesa"), safe_get_int(estatisticas["adr"], "ataque"), safe_get_int(estatisticas["adr"], "geral"),
            safe_get_simbol(estatisticas["hs"], "defesa"), safe_get_simbol(estatisticas["hs"], "ataque"), safe_get_simbol(estatisticas["hs"], "geral"),
            safe_get_int(estatisticas["fk"], "defesa"), safe_get_int(estatisticas["fk"], "ataque"), safe_get_int(estatisticas["fk"], "geral"),
            safe_get_int(estatisticas["fd"], "defesa"), safe_get_int(estatisticas["fd"], "ataque"), safe_get_int(estatisticas["fd"], "geral"),
            safe_get_simbol(estatisticas["fkfd+-"], "defesa"), safe_get_simbol(estatisticas["fkfd+-"], "ataque"), safe_get_simbol(estatisticas["fkfd+-"], "geral")
        )
    )
    with conn.cursor() as cursor:
        try:
            cursor.execute("BEGIN;")
            cursor.execute(query[0], query[1])
            result = cursor.fetchone()
            cursor.execute("COMMIT;")
            if result:
                id_partida_jogador = result[0]

        except Exception as e:
            cursor.execute("ROLLBACK;")
            logging.error(
                f"Error executing partida_jogador insert: {(id_partida, id_jogador, agente, estatisticas)} : {str(e)}"
            )
            raise
    return id_partida_jogador




def geraScript(dataframe, conn):
    for index, row in df.iterrows():
        # CAMPEONATOS
        campeonato_completo = ast.literal_eval(row["campeonato"])
        id_campeonato = insereCampeonato(conn, campeonato_completo)
        #print(f"ID camp: {id_campeonato}")

        # TIMES
        primeiroTime = row["nomePrimeiroTime"]
        segundoTime = row["nomeSegundoTime"]
        id_time_um = insereTimes(conn, primeiroTime)
        id_time_dois = insereTimes(conn, segundoTime)
        #print(id_time_um)
        #print(id_time_dois)

        # SEQUENCIA PARTIDA
        url = row["url"]
        datetime_str = row["date"]
        datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        tipo_partida = row["tipo_partida"]
        patch = extract_patch_info(row["patch"])

        id_seq_partida = insereSequenciaPartidas(
            conn,
            id_campeonato,
            datetime_obj,
            patch,
            tipo_partida,
            id_time_um,
            id_time_dois,
            url,
        )
        #print(f"id da sp:{id_seq_partida}")

        mapas_partidas = transformaRounds(row["mapas"])
        rounds_partidas = transformaRounds(row["rounds"])

        estatistica_partidas_tratadas = trataEstatisiticas(row["estatisticas"])
        #print(mapas_partidas)
        #print(rounds_partidas)

        for i in range(0, len(estatistica_partidas_tratadas), 2):
            rounds_partida = rounds_partidas[i // 2]
            vencedor_partida = criaLabelVencedor(rounds_partida)
            mapa_partida = mapas_partidas[i // 2]
            id_time_vencedor = None
            if vencedor_partida == "TIME1":
                id_time_vencedor = id_time_um
            else:
                id_time_vencedor = id_time_dois

            # PARTIDA
            id_partida = inserePartida(
                conn, id_seq_partida, mapa_partida, id_time_vencedor
            )

            # ROUND PARTIDA
            id_round_partida = insereRoundsPartida(conn, id_partida, rounds_partida)

            #print(id_partida)
            #print(id_round_partida)

            # Acessando TIME 1
            for j in estatistica_partidas_tratadas[i]:
                nomeJogador = removeTimeDoNome(j["name"])
                #print(nomeJogador)
                id_jogador = insereJogador(conn, nomeJogador, id_time_um)
                #print(f"id jogador: {id_jogador}")

                # agente = j["agente"]
                # print(f"id agente: {agente}")

                #print(j)
                id_partida_jogador = inserePartidaJogador(
                    conn, id_partida, id_jogador, j["agente"], j
                )
                #print(f"id partida jogador: {id_partida_jogador}")

            # Acessando TIME 2
            for j in estatistica_partidas_tratadas[i + 1]:
                nomeJogador = removeTimeDoNome(j["name"])
                id_jogador = insereJogador(conn, nomeJogador, id_time_dois)
                #print(f"id jogador: {id_jogador}")


                id_partida_jogador = inserePartidaJogador(
                    conn, id_partida, id_jogador, j["agente"], j
                )
                #print(f"id partida jogador: {id_partida_jogador}")

        break

def executaScript():
    conn = connect_db()
    try:
        geraScript(df, conn)
    finally:
        conn.close()


all_inserts = executaScript()
