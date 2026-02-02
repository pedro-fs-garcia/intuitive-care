CREATE DOMAIN uf_brasil AS CHAR(2)
CHECK (
    VALUE IN (
        'AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG',
        'PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO'
    )
);

CREATE TABLE operadoras (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    cnpj VARCHAR(14) NOT NULL UNIQUE,
    razao_social VARCHAR(255) NOT NULL,
    registro_ans VARCHAR(20),
    modalidade VARCHAR(100),
    uf uf_brasil NOT NULL
);
CREATE INDEX ON operadoras (razao_social);

CREATE TABLE despesas_consolidadas (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    operadora_id INT NOT NULL REFERENCES operadoras(id) ON DELETE CASCADE,
    trimestre INT NOT NULL,
    ano INT NOT NULL,
    valor_despesa DECIMAL(18, 2) NOT NULL
);
CREATE INDEX ON despesas_consolidadas (operadora_id, ano, trimestre);

CREATE TABLE despesas_agregadas (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    operadora_id INT NOT NULL REFERENCES operadoras(id) ON DELETE CASCADE,
    uf uf_brasil NOT NULL,
    total_despesas DECIMAL(18, 2),
    media_trimestral DECIMAL(18, 2),
    desvio_padrao DECIMAL(18, 2),
    qtd_trimestres INT
);
