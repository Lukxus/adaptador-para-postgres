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
    match = re.search(r"Patch (\d+(\.\d+)?)", text)
    if match:
        return match.group(0)
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
            logging.error(f"Error executing campeonato insert: {campeonatoLista} : {str(e)}")
            raise
    return id_campeonato

def transformaRounds(rounds):
    lista = ast.literal_eval(rounds)
    return lista

def criaLabelVencedor(rounds_lista):
    timeUm = sum(1 for round in rounds_lista if round <= 4)
    timeDois = sum(1 for round in rounds_lista if round > 4)
    return "TIME1" if timeUm > timeDois else "TIME2"

def insereTimes(conn, time):
    id_time = ""
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
                id_time = result[0]
        except Exception as e:
            cursor.execute("ROLLBACK;")
            logging.error(f"Error executing time insert: {time} : {str(e)}")
            raise
    return id_time

def insereSequenciaPartidas(conn, campeonato, data, patch, tipo, id_time1, id_time2, url):
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
            logging.error(f"Error executing sequencia_partida insert: {(campeonato, data, patch, tipo, id_time1, id_time2, url)} : {str(e)}")
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
            logging.error(f"Error executing partida insert: {(id_sequencia_partida, mapa, id_time_vencedor)} : {str(e)}")
            raise
    return id_partida

def trataEstatisiticas(estatisticas):
    dicionario = ast.literal_eval(estatisticas)
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
            logging.error(f"Error executing rounds_partida insert: {(id_partida, lista_de_resultados)} : {str(e)}")
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
            logging.error(f"Error executing jogador insert: {(nome, id_time)} : {str(e)}")
            raise
    return id_jogador

def removeTimeDoNome(name):
    if name:
        ultimo_espaco = name.rfind(" ")
        return name[:ultimo_espaco] if ultimo_espaco != -1 else name

def inserePartidaJogador(conn, id_partida, id_jogador, id_agente, stats):
    def get_stat_value(stat_dict, key, is_float=False):
        value = stat_dict.get(key)
        if value in [None, "", "None"]:
            return None
        if isinstance(value, str) and value.endswith("%"):
            try:
                return float(value.rstrip("%")) / 100
            except ValueError:
                return None
        if isinstance(value, str) and (value.startswith("+") or value.startswith("-")):
            try:
                return float(value) if is_float else int(value)
            except ValueError:
                return None
        try:
            return float(value) if is_float else int(value)
        except ValueError:
            return None

    query = """
        INSERT INTO Partida_Jogador (
            ID_partida, ID_jogador, ID_agente,
            R_defesa, R_ataque, R_geral,
            ACS_defesa, ACS_ataque, ACS_geral,
            K_defesa, K_ataque, K_geral,
            D_defesa, D_ataque, D_geral,
            A_defesa, A_ataque, A_geral,
            KDA_defesa, KDA_ataque, KDA_geral,
            KAST_defesa, KAST_ataque, KAST_geral,
            ADR_defesa, ADR_ataque, ADR_geral,
            HS_defesa, HS_ataque, HS_geral,
            FK_defesa, FK_ataque, FK_geral,
            FD_defesa, FD_ataque, FD_geral,
            FKFD_defesa, FKFD_ataque, FKFD_geral
        ) VALUES (
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s
        ) RETURNING ID;
    """
    params = (
        id_partida,
        id_jogador,
        id_agente,
        get_stat_value(stats.get("r", {}), "defesa"),
        get_stat_value(stats.get("r", {}), "ataque"),
        get_stat_value(stats.get("r", {}), "geral"),
        get_stat_value(stats.get("acs", {}), "defesa"),
        get_stat_value(stats.get("acs", {}), "ataque"),
        get_stat_value(stats.get("acs", {}), "geral"),
        get_stat_value(stats.get("k", {}), "defesa"),
        get_stat_value(stats.get("k", {}), "ataque"),
        get_stat_value(stats.get("k", {}), "geral"),
        get_stat_value(stats.get("d", {}), "defesa"),
        get_stat_value(stats.get("d", {}), "ataque"),
        get_stat_value(stats.get("d", {}), "geral"),
        get_stat_value(stats.get("a", {}), "defesa"),
        get_stat_value(stats.get("a", {}), "ataque"),
        get_stat_value(stats.get("a", {}), "geral"),
        get_stat_value(stats.get("kda+-", {}), "defesa", is_float=True),
        get_stat_value(stats.get("kda+-", {}), "ataque", is_float=True),
        get_stat_value(stats.get("kda+-", {}), "geral", is_float=True),
        get_stat_value(stats.get("kast", {}), "defesa", is_float=True),
        get_stat_value(stats.get("kast", {}), "ataque", is_float=True),
        get_stat_value(stats.get("kast", {}), "geral", is_float=True),
        get_stat_value(stats.get("adr", {}), "defesa", is_float=True),
        get_stat_value(stats.get("adr", {}), "ataque", is_float=True),
        get_stat_value(stats.get("adr", {}), "geral", is_float=True),
        get_stat_value(stats.get("hs", {}), "defesa", is_float=True),
        get_stat_value(stats.get("hs", {}), "ataque", is_float=True),
        get_stat_value(stats.get("hs", {}), "geral", is_float=True),
        get_stat_value(stats.get("fk", {}), "defesa"),
        get_stat_value(stats.get("fk", {}), "ataque"),
        get_stat_value(stats.get("fk", {}), "geral"),
        get_stat_value(stats.get("fd", {}), "defesa"),
        get_stat_value(stats.get("fd", {}), "ataque"),
        get_stat_value(stats.get("fd", {}), "geral"),
        get_stat_value(stats.get("fkfd+-", {}), "defesa", is_float=True),
        get_stat_value(stats.get("fkfd+-", {}), "ataque", is_float=True),
        get_stat_value(stats.get("fkfd+-", {}), "geral", is_float=True),
    )

    logging.info(f"Params for inserePartidaJogador: {params}")

    with conn.cursor() as cursor:
        try:
            cursor.execute("BEGIN;")
            cursor.execute(query, params)
            result = cursor.fetchone()
            cursor.execute("COMMIT;")
            return result[0] if result else None
        except Exception as e:
            cursor.execute("ROLLBACK;")
            logging.error(f"Error executing partida_jogador insert: {stats} : {str(e)}")
            raise

def geraScript(dataframe, conn):
    for index, row in df.iterrows():
        # CAMPEONATOS
        campeonato_completo = ast.literal_eval(row["campeonato"])
        id_campeonato = insereCampeonato(conn, campeonato_completo)
        logging.info(f"ID camp: {id_campeonato}")

        # TIMES
        primeiroTime = row["nomePrimeiroTime"]
        segundoTime = row["nomeSegundoTime"]
        id_time_um = insereTimes(conn, primeiroTime)
        id_time_dois = insereTimes(conn, segundoTime)
        logging.info(f"id_time_um: {id_time_um}")
        logging.info(f"id_time_dois: {id_time_dois}")

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
        logging.info(f"id_seq_partida: {id_seq_partida}")

        mapas_partidas = transformaRounds(row["mapas"])
        rounds_partidas = transformaRounds(row["rounds"])
        estatistica_partidas_tratadas = trataEstatisiticas(row["estatisticas"])

        for i in range(0, len(estatistica_partidas_tratadas), 2):
            rounds_partida = rounds_partidas[i // 2]
            vencedor_partida = criaLabelVencedor(rounds_partida)
            mapa_partida = mapas_partidas[i // 2]
            id_time_vencedor = id_time_um if vencedor_partida == "TIME1" else id_time_dois

            # PARTIDA
            id_partida = inserePartida(conn, id_seq_partida, mapa_partida, id_time_vencedor)
            logging.info(f"id_partida: {id_partida}")

            # ROUND PARTIDA
            id_round_partida = insereRoundsPartida(conn, id_partida, rounds_partida)
            logging.info(f"id_round_partida: {id_round_partida}")

            # Acessando TIME 1
            for j in estatistica_partidas_tratadas[i]:
                nomeJogador = removeTimeDoNome(j["name"])
                logging.info(f"nomeJogador: {nomeJogador}")
                id_jogador = insereJogador(conn, nomeJogador, id_time_um)
                logging.info(f"id_jogador: {id_jogador}")

                id_agente = insereAgente(conn, j["agente"])
                logging.info(f"id_agente: {id_agente}")

                logging.info(j)
                id_partida_jogador = inserePartidaJogador(
                    conn, id_partida, id_jogador, id_agente, j
                )
                logging.info(f"id_partida_jogador: {id_partida_jogador}")

        break

def insereAgente(conn, nome):
    id_agente = None
    insert_query = (
        "INSERT INTO Agente (Nome) VALUES (%s) "
        "ON CONFLICT (Nome) DO NOTHING "
        "RETURNING ID;",
        (nome,),
    )
    select_query = ("SELECT ID FROM Agente WHERE Nome = %s;", (nome,))
    with conn.cursor() as cursor:
        try:
            cursor.execute("BEGIN;")
            cursor.execute(insert_query[0], insert_query[1])
            result = cursor.fetchone()
            if result:
                id_agente = result[0]
            else:
                cursor.execute(select_query[0], select_query[1])
                result = cursor.fetchone()
                if result:
                    id_agente = result[0]
            cursor.execute("COMMIT;")
        except Exception as e:
            cursor.execute("ROLLBACK;")
            logging.error(f"Error executing agente insert: {nome} : {str(e)}")
            raise
    return id_agente

def executaScript():
    conn = connect_db()
    try:
        geraScript(df, conn)
    finally:
        conn.close()

executaScript()
