import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from sqlalchemy import create_engine, text

from database.db_session import engine
from .settings import PG_DATABASE, PG_URL, SQL_DIR, PATHS
from .models import Operadora, DespesaConsolidada, DespesaAgregada
from .db_session import SessionLocal



def init_db() -> None:
    create_db_if_not_exists(PG_URL, PG_DATABASE)
    create_tables()
    load_data()


def create_db_if_not_exists(pg_url: str, db_name:str) -> None:
    temp_engine = create_engine(pg_url, isolation_level="AUTOCOMMIT")
    with temp_engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :db"),
            {"db": db_name},
        )
        if not result.fetchone():
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            print(f"Banco '{db_name}' criado.")
        else:
            print(f"Banco '{db_name}' já existe")
    temp_engine.dispose()


def create_tables() -> None:
    schema_file = SQL_DIR / "db_schema.sql"

    with open(schema_file) as f:
        schema_sql = f.read()

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS despesas_agregadas CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS despesas_consolidadas CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS operadoras CASCADE"))
        conn.execute(text("DROP DOMAIN IF EXISTS uf_brasil CASCADE"))

        for statement in schema_sql.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))

    print("Tabelas Criadas")


def load_operadoras(db) -> None:
    if PATHS["operadoras"].exists():
        print(f"Carregando operadoras de {PATHS['operadoras']}")
        df_op = pd.read_csv(PATHS["operadoras"], sep=";", encoding="utf-8", dtype=str)
        
        for _, row in df_op.iterrows():
            cnpj = str(row.get("CNPJ", "")).replace(".", "").replace("/", "").replace("-", "")
            cnpj = cnpj.zfill(14)
            if not cnpj or len(cnpj) != 14:
                continue
                
            operadora = Operadora(
                cnpj=cnpj,
                razao_social=str(row.get("Razao_Social", "")),
                registro_ans=str(row.get("REG_ANS", "")) or None,
                modalidade=str(row.get("Modalidade", "")) or None,
                uf=str(row.get("UF", ""))[:2].upper(),
            )
            db.merge(operadora)
        
        db.commit()
        print(f"Operadoras carregadas: {db.query(Operadora).count()}")


def load_consolidado(db) -> None:
    if PATHS["consolidado"].exists():
        print(f"Carregando despesas consolidadas de {PATHS['consolidado']}")
        df_desp = pd.read_csv(PATHS["consolidado"], sep=";", encoding="utf-8", dtype=str)
        
        for _, row in df_desp.iterrows():
            cnpj = str(row.get("CNPJ", "")).replace(".", "").replace("/", "").replace("-", "")
            cnpj = cnpj.zfill(14)
            operadora = db.query(Operadora).filter(Operadora.cnpj == cnpj).first()
            
            if not operadora:
                continue
            
            valor_str = str(row.get("ValorDespesas", "0")).replace(".", "").replace(",", ".")
            try:
                valor = float(valor_str)
            except ValueError:
                valor = 0.0
            
            despesa = DespesaConsolidada(
                operadora_id=operadora.id,
                trimestre=int(row.get("Trimestre", 0)),
                ano=int(row.get("Ano", 0)),
                valor_despesa=valor,
            )
            db.add(despesa)
        
        db.commit()
        print(f"Despesas consolidadas carregadas: {db.query(DespesaConsolidada).count()}")
    

def load_agregados(db) -> None:
    if PATHS["agregado"].exists():
        print(f"Carregando despesas agregadas de {PATHS['agregado']}")
        df_agg = pd.read_csv(PATHS["agregado"], sep=";", encoding="utf-8", dtype=str)
        
        for _, row in df_agg.iterrows():
            cnpj = str(row.get("CNPJ", "")).replace(".", "").replace("/", "").replace("-", "")
            cnpj = cnpj.zfill(14)
            operadora = db.query(Operadora).filter(Operadora.cnpj == cnpj).first()
            
            if not operadora:
                continue
            
            def parse_decimal(val: str) -> float:
                try:
                    return float(str(val).replace(".", "").replace(",", "."))
                except (ValueError, TypeError):
                    return 0.0
            
            despesa_agg = DespesaAgregada(
                operadora_id=operadora.id,
                uf=str(row.get("UF", ""))[:2].upper(),
                total_despesas=parse_decimal(row.get("TotalDespesas", "0")),
                media_trimestral=parse_decimal(row.get("MediaTrimestral", "0")),
                desvio_padrao=parse_decimal(row.get("DesvioPadrao", "0")),
                qtd_trimestres=int(row.get("QtdTrimestres", 0)) if row.get("QtdTrimestres") else 0,
            )
            db.add(despesa_agg)
        
        db.commit()
        print(f"Despesas agregadas carregadas: {db.query(DespesaAgregada).count()}")
    


def load_data() -> None:
    db = SessionLocal()
    
    try:
        load_operadoras(db)        
        load_consolidado(db)
        load_agregados(db)
        print("Inserção de dados concluída!")
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao carregar dados: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
