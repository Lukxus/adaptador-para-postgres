-- Script para criar as tabelas

-- Tabela Campeonatos
CREATE TABLE Campeonatos (
    ID SERIAL PRIMARY KEY,
    Nome VARCHAR(255) NOT NULL
);

-- Tabela Times
CREATE TABLE Times (
    ID SERIAL PRIMARY KEY,
    Nome VARCHAR(255) NOT NULL
);

-- Tabela Mapa
CREATE TABLE Mapa (
    ID SERIAL PRIMARY KEY,
    Nome VARCHAR(255) NOT NULL
);

-- Tabela Partida
CREATE TABLE Partida (
    ID SERIAL PRIMARY KEY,
    Campeonato INT,
    Data TIMESTAMP NOT NULL,
    Patch VARCHAR(50) NOT NULL,
    Tipo VARCHAR(255) NOT NULL,
    FOREIGN KEY (Campeonato) REFERENCES Campeonatos(ID)
);

-- Tabela Rounds
CREATE TABLE Rounds (
    ID SERIAL PRIMARY KEY,
    ID_Mapa INT,
    FOREIGN KEY (ID_Mapa) REFERENCES Mapa(ID)
);

-- Tabela Rounds_Partida
CREATE TABLE Rounds_Partida (
    ID SERIAL PRIMARY KEY,
    ID_partida INT,
    ID_round INT,
    FOREIGN KEY (ID_partida) REFERENCES Partida(ID),
    FOREIGN KEY (ID_round) REFERENCES Rounds(ID)
);

-- Tabela Jogadores
CREATE TABLE Jogadores (
    ID SERIAL PRIMARY KEY,
    Nome VARCHAR(255) NOT NULL,
    ID_time INT,
    FOREIGN KEY (ID_time) REFERENCES Times(ID)
);

-- Tabela Agente
CREATE TABLE Agente (
    ID SERIAL PRIMARY KEY,
    Nome VARCHAR(255) NOT NULL
);

-- Tabela Rounds_Jogador
CREATE TABLE Rounds_Jogador (
    ID SERIAL PRIMARY KEY,
    ID_jogador INT,
    ID_round INT,
    ID_agente INT,
    R_defesa INT,
    R_ataque INT,
    R_geral INT,
    ACS_defesa VARCHAR(10),
    ACS_ataque VARCHAR(10),
    ACS_geral VARCHAR(10),
    K_defesa INT,
    K_ataque INT,
    K_geral INT,
    D_defesa INT,
    D_ataque INT,
    D_geral INT,
    A_defesa INT,
    A_ataque INT,
    A_geral INT,
    KDA_+/-_defesa VARCHAR(10),
    KDA_+/-_ataque VARCHAR(10),
    KDA_+/-_geral VARCHAR(10),
    KAST_defesa VARCHAR(10),
    KAST_ataque VARCHAR(10),
    KAST_geral VARCHAR(10),
    ADR_defesa VARCHAR(10),
    ADR_ataque VARCHAR(10),
    ADR_geral VARCHAR(10),
    HS%_defesa VARCHAR(10),
    HS%_ataque VARCHAR(10),
    HS%_geral VARCHAR(10),
    FK_defesa INT,
    FK_ataque INT,
    FK_geral INT,
    FD_defesa VARCHAR(10),
    FD_ataque VARCHAR(10),
    FD_geral VARCHAR(10),
    FKFD+/-_defesa VARCHAR(10),
    FKFD+/-_ataque VARCHAR(10),
    FKFD+/-_geral VARCHAR(10),
    FOREIGN KEY (ID_jogador) REFERENCES Jogadores(ID),
    FOREIGN KEY (ID_round) REFERENCES Rounds(ID),
    FOREIGN KEY (ID_agente) REFERENCES Agente(ID)
);
