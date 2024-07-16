import pandas as pd

# Carregar o arquivo CSV
file_path = r'D:\\Documents\\vlrcorte\\dados.csv'
df = pd.read_csv(file_path)

# Função para gerar script de insert para a tabela Campeonatos
def generate_campeonatos_insert(df):
    campeonatos = df['campeonato'].apply(lambda x: eval(x)[0]).unique()
    insert_statements = []
    for campeonato in campeonatos:
        insert_statements.append(f"INSERT INTO Campeonatos (Nome) VALUES ('{campeonato}');")
    return insert_statements

# Função para gerar script de insert para a tabela Times
def generate_times_insert(df):
    times = pd.concat([df['nomePrimeiroTime'], df['nomeSegundoTime']]).unique()
    insert_statements = []
    for time in times:
        insert_statements.append(f"INSERT INTO Times (Nome) VALUES ('{time}');")
    return insert_statements

# Função para gerar script de insert para a tabela Mapa
def generate_mapa_insert(df):
    mapas = df['mapas'].apply(lambda x: eval(x)).explode().unique()
    insert_statements = []
    for mapa in mapas:
        if mapa != 'N/A':
            insert_statements.append(f"INSERT INTO Mapa (Nome) VALUES ('{mapa}');")
    return insert_statements

# Função para gerar script de insert para a tabela Partida
def generate_partida_insert(df):
    insert_statements = []
    for index, row in df.iterrows():
        campeonato = eval(row['campeonato'])[0]
        insert_statements.append(
            f"INSERT INTO Partida (Campeonato, Data, Patch, Tipo) VALUES "
            f"((SELECT ID FROM Campeonatos WHERE Nome = '{campeonato}'), '{row['date']}', '{row['patch']}', '{row['tipo_partida']}');"
        )
    return insert_statements

# Função para gerar script de insert para a tabela Rounds
def generate_rounds_insert(df):
    insert_statements = []
    round_id = 1
    for index, row in df.iterrows():
        mapas = eval(row['mapas'])
        rounds = eval(row['rounds'])
        for mapa, round_data in zip(mapas, rounds):
            if mapa != 'N/A':
                insert_statements.append(
                    f"INSERT INTO Rounds (ID_Mapa) VALUES "
                    f"((SELECT ID FROM Mapa WHERE Nome = '{mapa}'));"
                )
                for _ in round_data:
                    insert_statements.append(
                        f"INSERT INTO Rounds_Partida (ID_partida, ID_round) VALUES "
                        f"((SELECT ID FROM Partida WHERE Data = '{row['date']}' AND Patch = '{row['patch']}'), {round_id});"
                    )
                    round_id += 1
    return insert_statements

# Função para gerar script de insert para a tabela Jogadores e Rounds_Jogador
def generate_jogadores_and_rounds_jogador_insert(df):
    insert_statements = []
    for index, row in df.iterrows():
        partidas = eval(row['estatisticas'])
        for partida in partidas:
            for jogador in partida:
                insert_statements.append(
                    f"INSERT INTO Jogadores (Nome, ID_time) VALUES "
                    f"('{jogador['name']}', (SELECT ID FROM Times WHERE Nome = '{row['nomePrimeiroTime']}' OR Nome = '{row['nomeSegundoTime']}'));"
                )
                
                # Garantir que todas as chaves existem antes de acessá-las
                kda_defesa = jogador.get('kda', {}).get('+/-', {}).get('defesa', 'NULL')
                kda_ataque = jogador.get('kda', {}).get('+/-', {}).get('ataque', 'NULL')
                kda_geral = jogador.get('kda', {}).get('+/-', {}).get('geral', 'NULL')
                
                hs_defesa = jogador.get('hs%', {}).get('defesa', 'NULL')
                hs_ataque = jogador.get('hs%', {}).get('ataque', 'NULL')
                hs_geral = jogador.get('hs%', {}).get('geral', 'NULL')
                
                fkfd_defesa = jogador.get('fkfd+/-', {}).get('defesa', 'NULL')
                fkfd_ataque = jogador.get('fkfd+/-', {}).get('ataque', 'NULL')
                fkfd_geral = jogador.get('fkfd+/-', {}).get('geral', 'NULL')
                
                insert_statements.append(
                    f"INSERT INTO Rounds_Jogador (ID_jogador, ID_round, ID_agente, R_defesa, R_ataque, R_geral, ACS_defesa, ACS_ataque, ACS_geral, "
                    f"K_defesa, K_ataque, K_geral, D_defesa, D_ataque, D_geral, A_defesa, A_ataque, A_geral, KDA_+/-_defesa, KDA_+/-_ataque, "
                    f"KDA_+/-_geral, KAST_defesa, KAST_ataque, KAST_geral, ADR_defesa, ADR_ataque, ADR_geral, HS%_defesa, HS%_ataque, HS%_geral, "
                    f"FK_defesa, FK_ataque, FK_geral, FD_defesa, FD_ataque, FD_geral, FKFD+/-_defesa, FKFD+/-_ataque, FKFD+/-_geral) VALUES "
                    f"((SELECT ID FROM Jogadores WHERE Nome = '{jogador['name']}'), "
                    f"(SELECT ID FROM Rounds WHERE ID = {index + 1}), "
                    f"(SELECT ID FROM Agente WHERE Nome = '{jogador['agente']}'), "
                    f"{jogador['r']['defesa']}, {jogador['r']['ataque']}, {jogador['r']['geral']}, "
                    f"'{jogador['acs']['defesa']}', '{jogador['acs']['ataque']}', '{jogador['acs']['geral']}', "
                    f"{jogador['k']['defesa']}, {jogador['k']['ataque']}, {jogador['k']['geral']}, "
                    f"{jogador['d']['defesa']}, {jogador['d']['ataque']}, {jogador['d']['geral']}, "
                    f"{jogador['a']['defesa']}, {jogador['a']['ataque']}, {jogador['a']['geral']}, "
                    f"'{kda_defesa}', '{kda_ataque}', '{kda_geral}', "
                    f"'{jogador['kast']['defesa']}', '{jogador['kast']['ataque']}', '{jogador['kast']['geral']}', "
                    f"'{jogador['adr']['defesa']}', '{jogador['adr']['ataque']}', '{jogador['adr']['geral']}', "
                    f"'{hs_defesa}', '{hs_ataque}', '{hs_geral}', "
                    f"{jogador['fk']['defesa']}, {jogador['fk']['ataque']}, {jogador['fk']['geral']}, "
                    f"'{jogador['fd']['defesa']}', '{jogador['fd']['ataque']}', '{jogador['fd']['geral']}', "
                    f"'{fkfd_defesa}', '{fkfd_ataque}', '{fkfd_geral}');"
                )
    return insert_statements

# Gerar scripts de insert
campeonatos_inserts = generate_campeonatos_insert(df)
times_inserts = generate_times_insert(df)
mapa_inserts = generate_mapa_insert(df)
partida_inserts = generate_partida_insert(df)
rounds_inserts = generate_rounds_insert(df)
jogadores_and_rounds_jogador_inserts = generate_jogadores_and_rounds_jogador_insert(df)

# Unir todos os inserts
all_inserts = (
    campeonatos_inserts + times_inserts + mapa_inserts + partida_inserts + rounds_inserts + jogadores_and_rounds_jogador_inserts
)

# Função para dividir os comandos SQL em vários arquivos
def save_in_batches(inserts, batch_size, base_filename):
    total_inserts = len(inserts)
    for i in range(0, total_inserts, batch_size):
        batch_inserts = inserts[i:i + batch_size]
        filename = f"{base_filename}_part_{i//batch_size + 1}.sql"
        with open(filename, 'w', encoding='utf-8') as f:
            for insert in batch_inserts:
                f.write(insert + '\n')

# Salvar os inserts em arquivos SQL menores com codificação utf-8
# Ajuste o batch_size para reduzir o número de arquivos
save_in_batches(all_inserts, 300000, 'inserts')