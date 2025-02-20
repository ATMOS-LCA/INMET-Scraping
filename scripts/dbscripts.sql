CREATE TABLE inmet.dados_estacoes (
    id      SERIAL PRIMARY KEY,
    estacao TEXT NOT NULL,
    data    DATE NOT NULL,
    utc     TEXT NOT NULL,
    temperatura DECIMAL,
    umidade     DECIMAL,
    pto_orvalho DECIMAL,
    pressao     DECIMAL,
    vento       DECIMAL,
    radiacao    DECIMAL,
    chuva       DECIMAL,
    CONSTRAINT dados_estacoes_momento_uk UNIQUE (estacao, data, utc)
);