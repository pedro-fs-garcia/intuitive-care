import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import create_engine, text

from database.db_session import engine
from .settings import PG_DATABASE, PG_URL, SQL_DIR 



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


def load_data() -> None:
    ...


if __name__ == "__main__":
    init_db()
