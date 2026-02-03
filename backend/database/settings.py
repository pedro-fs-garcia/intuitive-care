import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


load_dotenv(Path(__file__).parent.parent.parent / ".env")

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_USER = os.getenv("PG_USER", "postgres")
_raw_password = os.getenv("PG_PASSWORD", "")
PG_PASSWORD = quote_plus(_raw_password)
PG_DATABASE = os.getenv("PG_DATABASE", "intuitive_care")


PG_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/postgres"
DB_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"


SQL_DIR = Path(__file__).parent.parent / "sql"
ROOT_DIR = Path(__file__).parent.parent.parent

PATHS = {
    "operadoras": ROOT_DIR / "data" / "operadoras" / "operadoras.csv",
    "consolidado": ROOT_DIR / "data" / "consolidado" / "consolidado_despesas.csv",
    "agregado": ROOT_DIR / "output" / "despesas_agregadas.csv",
}
