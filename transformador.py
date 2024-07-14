import pandas as pd

# Ler o CSV
csv_file = 'dados.csv'  # Atualize com o caminho correto do seu arquivo CSV
data = pd.read_csv(csv_file)

# Função para gerar SQL de inserção na tabela Campeonatos
def generate_insert_campeonato_sql(nome):
    return f"INSERT INTO Campeonatos (Nome) VALUES ('{nome}');\n"

# Função para gerar SQL de inserção na tabela Times
def generate_insert_time_sql(nome):
    return f"INSERT INTO Times (Nome) VALUES ('{nome}');\n"

# Função para gerar SQL de inserção na tabela Mapa
def generate_insert_mapa_sql(nome):
    return f"INSERT INTO Mapa (Nome) VALUES ('{nome}');\n"

# Função para gerar SQL de inserção na tabela Partida
def generate_insert_partida_sql(campeonato, data, patch, tipo):
    return f"INSERT INTO Partida (Campeonato, Data, Patch, Tipo) VALUES ('{campeonato}', '{data}', '{patch}', '{tipo}');\n"

# Função para gerar SQL de inserção na tabela Rounds
def generate_insert_round_sql(id_mapa):
    return f"INSERT INTO Rounds (ID_Mapa) VALUES ({id_mapa});\n"

# Função para gerar SQL de inserção na tabela Rounds Partida
def generate_insert_round_partida_sql(id_partida, id_round):
    return f"INSERT INTO Rounds_Partida (ID_partida, ID_round) VALUES ({id_partida}, {id_round});\n"

# Função para gerar SQL de inserção na tabela Jogadores
def generate_insert_jogador_sql(nome, id_time):
    return f"INSERT INTO Jogadores (Nome, ID_time) VALUES ('{nome}', {id_time});\n"

# Função para gerar SQL de inserção na tabela Agente
def generate_insert_agente_sql(nome):
    return f"INSERT INTO Agente (Nome) VALUES ('{nome}');\n"

# Função para gerar SQL de inserção na tabela Rounds Jogador
def generate_insert_round_jogador_sql(data):
    return f"""
    INSERT INTO Rounds_Jogador (
        ID_jogador, ID_round, ID_agente, R_defesa, R_ataque, R_geral, 
        ACS_defesa, ACS_ataque, ACS_geral, K_defesa, K_ataque, K_geral, 
        D_defesa, D_ataque, D_geral, A_defesa, A_ataque, A_geral, 
        KDA_+/-_defesa, KDA_+/-_ataque, KDA_+/-_geral, KAST_defesa, KAST_ataque, KAST_geral, 
        ADR_defesa, ADR_ataque, ADR_geral, HS%_defesa, HS%_ataque, HS%_geral, 
        FK_defesa, FK_ataque, FK_geral, FD_defesa, FD_ataque, FD_geral, 
        FKFD+/-_defesa, FKFD+/-_ataque, FKFD+/-_geral
    ) VALUES (
        {data['ID_jogador']}, {data['ID_round']}, {data['ID_agente']}, {data['R_defesa']}, {data['R_ataque']}, {data['R_geral']}, 
        '{data['ACS_defesa']}', '{data['ACS_ataque']}', '{data['ACS_geral']}', {data['K_defesa']}, {data['K_ataque']}, {data['K_geral']}, 
        {data['D_defesa']}, {data['D_ataque']}, {data['D_geral']}, {data['A_defesa']}, {data['A_ataque']}, {data['A_geral']}, 
        '{data['KDA_+/-_defesa']}', '{data['KDA_+/-_ataque']}', '{data['KDA_+/-_geral']}', '{data['KAST_defesa']}', '{data['KAST_ataque']}', '{data['KAST_geral']}', 
        '{data['ADR_defesa']}', '{data['ADR_ataque']}', '{data['ADR_geral']}', '{data['HS%_defesa']}', '{data['HS%_ataque']}', '{data['HS%_geral']}', 
        {data['FK_defesa']}, {data['FK_ataque']}, {data['FK_geral']}, '{data['FD_defesa']}', '{data['FD_ataque']}', '{data['FD_geral']}', 
        '{data['FKFD+/-_defesa']}', '{data['FKFD+/-_ataque']}', '{data['FKFD+/-_geral']}'
    );\n"""

# Gerar o script SQL
sql_script = ""

# Iterar sobre as linhas do CSV para gerar os comandos de inserção
for index, row in data.iterrows():
    # Inserir um campeonato
    campeonato_nome = row['Campeonato']
    sql_script += generate_insert_campeonato_sql(campeonato_nome)

    # Inserir times
    time1_nome = row['Time1']
    time2_nome = row['Time2']
    sql_script += generate_insert_time_sql(time1_nome)
    sql_script += generate_insert_time_sql(time2_nome)

    # Inserir mapas
    mapas = eval(row['Mapas'])
    for mapa in mapas:
        sql_script += generate_insert_mapa_sql(mapa)

    # Inserir partidas
    partida_data = row['Data']
    partida_patch = row['Patch']
    partida_tipo = row['Tipo']
    sql_script += generate_insert_partida_sql(campeonato_nome, partida_data, partida_patch, partida_tipo)

    # Inserir rounds e relacionar com partidas
    rounds = eval(row['Rounds'])
    for round_index, round_data in enumerate(rounds, start=1):
        sql_script += generate_insert_round_sql(round_index)
        sql_script += generate_insert_round_partida_sql(index + 1, round_index)  # Supondo que o ID da partida é o índice + 1

    # Inserir jogadores
    jogadores_time1 = eval(row['Jogadores_time1'])
    jogadores_time2 = eval(row['Jogadores_time2'])
    for jogador in jogadores_time1:
        sql_script += generate_insert_jogador_sql(jogador['name'], 1)  # Supondo que o ID do time 1 é 1
    for jogador in jogadores_time2:
        sql_script += generate_insert_jogador_sql(jogador['name'], 2)  # Supondo que o ID do time 2 é 2

    # Inserir agentes e estatísticas dos jogadores nos rounds
    for jogador in jogadores_time1 + jogadores_time2:
        agente_nome = jogador['agente']
        sql_script += generate_insert_agente_sql(agente_nome)
        round_jogador_data = {
            'ID_jogador': jogador['id'],  # Assumindo que o ID do jogador está no dicionário
            'ID_round': round_index,
            'ID_agente': 1,  # Assumindo que o ID do agente é 1 para todos
            'R_defesa': jogador['r']['defesa'],
            'R_ataque': jogador['r']['ataque'],
            'R_geral': jogador['r']['geral'],
            'ACS_defesa': jogador['acs']['defesa'],
            'ACS_ataque': jogador['acs']['ataque'],
            'ACS_geral': jogador['acs']['geral'],
            'K_defesa': jogador['k']['defesa'],
            'K_ataque': jogador['k']['ataque'],
            'K_geral': jogador['k']['geral'],
            'D_defesa': jogador['d']['defesa'],
            'D_ataque': jogador['d']['ataque'],
            'D_geral': jogador['d']['geral'],
            'A_defesa': jogador['a']['defesa'],
            'A_ataque': jogador['a']['ataque'],
            'A_geral': jogador['a']['geral'],
            'KDA_+/-_defesa': jogador['kda+-']['defesa'],
            'KDA_+/-_ataque': jogador['kda+-']['ataque'],
            'KDA_+/-_geral': jogador['kda+-']['geral'],
            'KAST_defesa': jogador['kast']['defesa'],
            'KAST_ataque': jogador['kast']['ataque'],
            'KAST_geral': jogador['kast']['geral'],
            'ADR_defesa': jogador['adr']['defesa'],
            'ADR_ataque': jogador['adr']['ataque'],
            'ADR_geral': jogador['adr']['geral'],
            'HS%_defesa': jogador['hs']['defesa'],
            'HS%_ataque': jogador['hs']['ataque'],
            'HS%_geral': jogador['hs']['geral'],
            'FK_defesa': jogador['fk']['defesa'],
            'FK_ataque': jogador['fk']['ataque'],
            'FK_geral': jogador['fk']['geral'],
            'FD_defesa': jogador['fd']['defesa'],
            'FD_ataque': jogador['fd']['ataque'],
            'FD_geral': jogador['fd']['geral'],
            'FKFD+/-_defesa': jogador['fkfd+-']['defesa'],
            'FKFD+/-_ataque': jogador['fkfd+-']['ataque'],
            'FKFD+/-_geral': jogador['fkfd+-']['geral']
        }
        sql_script += generate_insert_round_jogador_sql(round_jogador_data)

# Salvar o script SQL em um arquivo
with open('inserts.sql', 'w') as file:
    file.write(sql_script)

print("Script SQL gerado com sucesso!")
