CREATE TABLE Campeonatos (
    ID SERIAL PRIMARY KEY,
    Nome VARCHAR(255) NOT NULL,
    Especificacao VARCHAR(255),
    UNIQUE (Nome, Especificacao)  -- Adiciona chave única
);

CREATE TABLE Times (
    ID SERIAL PRIMARY KEY,
    Nome VARCHAR(255) NOT NULL,
    UNIQUE (Nome)  -- Adiciona chave única
);

CREATE TABLE Sequencia_Partida (
    ID SERIAL PRIMARY KEY,
    Campeonato INT NOT NULL,
    Data TIMESTAMP NOT NULL,
    Patch VARCHAR(255) NOT NULL,
    Tipo INT NOT NULL,
    ID_time1 INT NOT NULL,
    ID_time2 INT NOT NULL,
    URL VARCHAR(255),
    FOREIGN KEY (Campeonato) REFERENCES Campeonatos(ID),
    FOREIGN KEY (ID_time1) REFERENCES Times(ID),
    FOREIGN KEY (ID_time2) REFERENCES Times(ID)
);

CREATE TABLE Partida (
    ID SERIAL PRIMARY KEY,
    ID_sequencia_partida INT NOT NULL,
    Mapa VARCHAR(255) NOT NULL,
    ID_time_vencedor INT,
    FOREIGN KEY (ID_sequencia_partida) REFERENCES Sequencia_Partida(ID),
    FOREIGN KEY (ID_time_vencedor) REFERENCES Times(ID)
);


CREATE TABLE Rounds_Partida (
    ID SERIAL PRIMARY KEY,
    ID_partida INT NOT NULL,
    Lista_de_resultados TEXT NOT NULL,
    FOREIGN KEY (ID_partida) REFERENCES Partida(ID)
);

CREATE TABLE Jogadores (
    ID SERIAL PRIMARY KEY,
    Nome VARCHAR(255) NOT NULL,
    ID_time INT NOT NULL,
    FOREIGN KEY (ID_time) REFERENCES Times(ID),
    UNIQUE (Nome, ID_time)  -- Adiciona chave única
);

CREATE TABLE Agente (
    ID SERIAL PRIMARY KEY,
    Nome VARCHAR(255) NOT NULL,
    UNIQUE (Nome)  -- Adiciona chave única
);

CREATE TABLE Partida_Jogador (
    ID SERIAL PRIMARY KEY,
    ID_partida INT NOT NULL,
    ID_jogador INT NOT NULL,
    ID_agente INT,
    R_defesa INT,
    R_ataque INT,
    R_geral INT,
    ACS_defesa INT,
    ACS_ataque INT,
    ACS_geral INT,
    K_defesa INT,
    K_ataque INT,
    K_geral INT,
    D_defesa INT,
    D_ataque INT,
    D_geral INT,
    A_defesa INT,
    A_ataque INT,
    A_geral INT,
    KDA_defesa FLOAT,
    KDA_ataque FLOAT,
    KDA_geral FLOAT,
    KAST_defesa FLOAT,
    KAST_ataque FLOAT,
    KAST_geral FLOAT,
    ADR_defesa FLOAT,
    ADR_ataque FLOAT,
    ADR_geral FLOAT,
    HS_defesa FLOAT,
    HS_ataque FLOAT,
    HS_geral FLOAT,
    FK_defesa INT,
    FK_ataque INT,
    FK_geral INT,
    FD_defesa INT,
    FD_ataque INT,
    FD_geral INT,
    FKFD_defesa FLOAT,
    FKFD_ataque FLOAT,
    FKFD_geral FLOAT,
    FOREIGN KEY (ID_partida) REFERENCES Partida(ID),
    FOREIGN KEY (ID_jogador) REFERENCES Jogadores(ID),
    FOREIGN KEY (ID_agente) REFERENCES Agente(ID)
);
