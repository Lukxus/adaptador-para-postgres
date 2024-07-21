import re
import ast

class DataProcessor:
    @staticmethod
    def extract_patch_info(text):
        match = re.search(r"Patch (\d+(\.\d+)?)", text)
        return match.group(0) if match else None

    @staticmethod
    def transforma_rounds(rounds):
        return ast.literal_eval(rounds)

    @staticmethod
    def cria_label_vencedor(rounds_lista):
        timeUm = sum(1 for round in rounds_lista if round <= 4)
        timeDois = sum(1 for round in rounds_lista if round > 4)
        return "TIME1" if timeUm > timeDois else "TIME2"

    @staticmethod
    def trata_estatisticas(estatisticas):
        return ast.literal_eval(estatisticas)

    @staticmethod
    def remove_time_do_nome(name):
        if name:
            ultimo_espaco = name.rfind(" ")
            return name[:ultimo_espaco] if ultimo_espaco != -1 else name
