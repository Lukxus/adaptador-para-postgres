import logging

class Inserter:
    def __init__(self, db):
        self.db = db

    def insere_campeonato(self, campeonatoLista):
        query = (
            "INSERT INTO Campeonatos (Nome, Especificacao) VALUES (%s, %s) "
            "ON CONFLICT (Nome, Especificacao) DO UPDATE SET Nome = EXCLUDED.Nome "
            "RETURNING ID;",
            (campeonatoLista[0], campeonatoLista[1]),
        )
        return self._execute_insert(query)

    def insere_times(self, time):
        query = (
            "INSERT INTO Times (Nome) VALUES (%s) "
            "ON CONFLICT (Nome) DO UPDATE SET Nome = EXCLUDED.Nome "
            "RETURNING ID;",
            (time,),
        )
        return self._execute_insert(query)

    def insere_sequencia_partidas(self, campeonato, data, patch, tipo, id_time1, id_time2, url):
        query = (
            "INSERT INTO Sequencia_Partida (Campeonato, Data, Patch, Tipo, ID_time1, ID_time2, URL) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s) "
            "RETURNING ID;",
            (campeonato, data, patch, tipo, id_time1, id_time2, url),
        )
        return self._execute_insert(query)

    def insere_partida(self, id_sequencia_partida, mapa, id_time_vencedor):
        query = (
            "INSERT INTO Partida (ID_sequencia_partida, Mapa, ID_time_vencedor) "
            "VALUES (%s, %s, %s) "
            "RETURNING ID;",
            (id_sequencia_partida, mapa, id_time_vencedor),
        )
        return self._execute_insert(query)

    def insere_rounds_partida(self, id_partida, lista_de_resultados):
        query = (
            "INSERT INTO Rounds_Partida (ID_partida, Lista_de_resultados) "
            "VALUES (%s, %s) "
            "RETURNING ID;",
            (id_partida, lista_de_resultados),
        )
        return self._execute_insert(query)

    def insere_jogador(self, nome, id_time):
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
        return self._execute_insert(insert_query, select_query)

    def insere_partida_jogador(self, conn, id_partida, id_jogador, agente, estatisticas):
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
            elif "%" in value:
                return int(value[:-1])
            return int(value)

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

    def _execute_insert(self, insert_query, select_query=None):
        result_id = None
        with self.db.conn.cursor() as cursor:
            try:
                cursor.execute("BEGIN;")
                cursor.execute(insert_query[0], insert_query[1])
                result = cursor.fetchone()
                if result:
                    result_id = result[0]
                elif select_query:
                    cursor.execute(select_query[0], select_query[1])
                    result = cursor.fetchone()
                    if result:
                        result_id = result[0]
                cursor.execute("COMMIT;")
            except Exception as e:
                cursor.execute("ROLLBACK;")
                logging.error(f"Error executing insert: {insert_query} : {str(e)}")
                raise
        return result_id
