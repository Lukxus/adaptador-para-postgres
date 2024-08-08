import logging

class Inserter:
    def __init__(self, db):
        self.db = db

    def insere_campeonato(self, campeonatoLista):
        query = (
            "INSERT INTO campeonato (nome_campeonato, especificacao_campeonato) VALUES (%s, %s) "
            "ON CONFLICT (nome_campeonato, especificacao_campeonato) DO UPDATE SET nome_campeonato = EXCLUDED.nome_campeonato "
            "RETURNING id;",
            (campeonatoLista[0], campeonatoLista[1]),
        )
        return self._execute_insert(query)

    def insere_times(self, time):
        query = (
            "INSERT INTO time (nome_time) VALUES (%s) "
            "ON CONFLICT (nome_time) DO UPDATE SET nome_time = EXCLUDED.nome_time "
            "RETURNING id;",
            (time,),
        )
        return self._execute_insert(query)

    def insere_sequencia_partidas(self, campeonato, data, patch, tipo, id_time1, id_time2, url):
        query = (
            "INSERT INTO sequencia_partida (id_campeonato, data_partida, patch_partida, tipo_partida, id_time1, id_time2, url_partida) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s) "
            "RETURNING id;",
            (campeonato, data, patch, tipo, id_time1, id_time2, url),
        )
        return self._execute_insert(query)

    def insere_partida(self, id_sequencia_partida, mapa, id_time_vencedor):
        query = (
            "INSERT INTO partida (id_sequencia_partida, mapa_partida, id_time_vencedor) "
            "VALUES (%s, %s, %s) "
            "RETURNING id;",
            (id_sequencia_partida, mapa, id_time_vencedor),
        )
        return self._execute_insert(query)

    def insere_rounds_partida(self, id_partida, lista_de_resultados):
        query = (
            "INSERT INTO rounds_partida (id_partida, resultados_rounds) "
            "VALUES (%s, %s) "
            "RETURNING id;",
            (id_partida, lista_de_resultados),
        )
        return self._execute_insert(query)

    def insere_jogador(self, nome, id_time):
        insert_query = (
            "INSERT INTO jogador (nome_jogador, id_time) "
            "VALUES (%s, %s) "
            "ON CONFLICT (nome_jogador, id_time) DO NOTHING "
            "RETURNING id;",
            (nome, id_time),
        )
        select_query = (
            "SELECT id FROM jogador WHERE nome_jogador = %s AND id_time = %s;",
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
            elif "," in value:
                value = value.replace(",", "")
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
            "INSERT INTO partida_jogador (id_partida, id_jogador, agente_jogador, r_defesa, r_ataque, r_geral, acs_defesa, acs_ataque, acs_geral, "
            "k_defesa, k_ataque, k_geral, d_defesa, d_ataque, d_geral, a_defesa, a_ataque, a_geral, kda_defesa, kda_ataque, kda_geral, "
            "kast_defesa, kast_ataque, kast_geral, adr_defesa, adr_ataque, adr_geral, hs_defesa, hs_ataque, hs_geral, fk_defesa, fk_ataque, "
            "fk_geral, fd_defesa, fd_ataque, fd_geral, fkfd_defesa, fkfd_ataque, fkfd_geral) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
            "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            "RETURNING id;",
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
