import pandas as pd
import logging
import ast
from datetime import datetime
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from database import Database
from dataprocessor import DataProcessor
from inserter import Inserter
from tqdm import tqdm  # Importando a barra de progresso

logging.basicConfig(
    filename="db_inserts.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(message)s",
)


class ScriptExecutor:
    def __init__(self, db, df):
        self.db = db
        self.df = df
        self.inserter = Inserter(db)

    def execute(self):
        for index, row in tqdm(self.df.iterrows(), total=self.df.shape[0], desc="Processing Rows"):

            # Partidas com Tipo Incorreto:
            url = row["url"]

            valores_a_dropar = [
                "https://www.vlr.gg/124758/b4-angels-vs-gamelanders-purple-gamers-club-elite-cup-immortal-r3",
                "https://www.vlr.gg/124732/team-liquid-brazil-vs-oddik-bright-gamers-club-elite-cup-immortal-r3",
                "https://www.vlr.gg/163068/refre5h-vs-rpg-challengers-league-portugal-split-1-5th-place",
            ]
            if url in valores_a_dropar:
                continue

            # CAMPEONATOS
            campeonato_completo = ast.literal_eval(row["campeonato"])
            id_campeonato = self.inserter.insere_campeonato(campeonato_completo)

            # TIMES
            primeiroTime = row["nomePrimeiroTime"]
            segundoTime = row["nomeSegundoTime"]
            id_time_um = self.inserter.insere_times(primeiroTime)
            id_time_dois = self.inserter.insere_times(segundoTime)

            # SEQUENCIA PARTIDA
            datetime_str = row["date"]
            datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            tipo_partida = row["tipo_partida"]
            if pd.isna(row["patch"]):
                patch = ""
            else:
                patch = DataProcessor.extract_patch_info(row["patch"])

            id_seq_partida = self.inserter.insere_sequencia_partidas(
                id_campeonato,
                datetime_obj,
                patch,
                tipo_partida,
                id_time_um,
                id_time_dois,
                url,
            )

            mapas_partidas = DataProcessor.transforma_rounds(row["mapas"])
            rounds_partidas = DataProcessor.transforma_rounds(row["rounds"])
            estatistica_partidas_tratadas = DataProcessor.trata_estatisticas(
                row["estatisticas"]
            )

            for i in range(0, len(estatistica_partidas_tratadas), 2):
                rounds_partida = rounds_partidas[i // 2]
                vencedor_partida = DataProcessor.cria_label_vencedor(rounds_partida)
                mapa_partida = mapas_partidas[i // 2]
                id_time_vencedor = (
                    id_time_um if vencedor_partida == "TIME1" else id_time_dois
                )

                # PARTIDA
                id_partida = self.inserter.insere_partida(
                    id_seq_partida, mapa_partida, id_time_vencedor
                )

                # ROUND PARTIDA
                self.inserter.insere_rounds_partida(id_partida, rounds_partida)

                # Acessando TIME 1
                for j in estatistica_partidas_tratadas[i]:
                    nomeJogador = DataProcessor.remove_time_do_nome(j["name"])
                    id_jogador = self.inserter.insere_jogador(nomeJogador, id_time_um)
                    self.inserter.insere_partida_jogador(
                        self.db.conn, id_partida, id_jogador, j["agente"], j
                    )

                # Acessando TIME 2
                for j in estatistica_partidas_tratadas[i + 1]:
                    nomeJogador = DataProcessor.remove_time_do_nome(j["name"])
                    id_jogador = self.inserter.insere_jogador(nomeJogador, id_time_dois)
                    self.inserter.insere_partida_jogador(
                        self.db.conn, id_partida, id_jogador, j["agente"], j
                    )


if __name__ == "__main__":
    file_path = r"/Users/luizsaraiva/Downloads/dados.csv"
    df = pd.read_csv(file_path)
    db = Database(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
    db.connect()
    try:
        executor = ScriptExecutor(db, df)
        executor.execute()
    finally:
        db.close()
