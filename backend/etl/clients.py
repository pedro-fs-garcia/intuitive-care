import io
import re
from pathlib import Path

import pandas as pd
import requests

from .constants import constant_paths
from .libs import ZipHandler


class LocalStorageClient:
    SUPPORTED_EXTENSIONS = {".csv", ".txt", ".xlsx", ".xls"}

    def __init__(self, zip_handler: ZipHandler):
        self.zip_handler = zip_handler

    def save_files(self, files_bytes: dict[str, io.BytesIO], output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        for name, bytes in files_bytes.items():
            path = output_dir / name
            bytes.seek(0)
            with open(path, "wb") as f:
                f.write(bytes.read())

    def save_csv_from_df(self, df: pd.DataFrame, output_dir: Path, file_name: str) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(
            output_dir / file_name,
            sep=";",
            decimal=",",
            encoding="utf-8",
            index=False,
        )

    def save_zip_csv_from_df(
        self, df: pd.DataFrame, output_dir: Path, zip_name: str, csv_name: str
    ) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        self.zip_handler.export_df_to_zip(df, output_dir, zip_name, csv_name)

    def read(self, file_path: Path) -> pd.DataFrame:
        """Lê arquivo detectando formato automaticamente pela extensão."""
        extension = file_path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Formato não suportado: {extension}")

        print(f"Lendo arquivo {file_path.name} (formato: {extension})")

        if extension in {".xlsx", ".xls"}:
            return self._read_excel(file_path)
        return self._read_csv(file_path)

    def _read_excel(self, file_path: Path) -> pd.DataFrame:
        df = pd.read_excel(file_path, engine="openpyxl")
        print(f"{len(df)} linhas")
        return df

    def _read_csv(self, file_path: Path) -> pd.DataFrame:
        encodings = ["utf-8", "latin1", "cp1252"]
        separators = [";", ",", "\t", "|"]

        for encoding in encodings:
            for sep in separators:
                try:
                    df = pd.read_csv(
                        file_path,
                        sep=sep,
                        encoding=encoding,
                        decimal=",",
                        low_memory=False,
                    )
                    if len(df.columns) > 1:
                        print(f"encoding={encoding}, sep='{sep}', {len(df)} linhas")
                        return df
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue

        raise ValueError(f"Não foi possível ler o arquivo: {file_path}")

    def extract_despesas_consolidate_df(self) -> pd.DataFrame:
        self.zip_handler.extract_local_file(
            constant_paths.output_dir / "consolidado_despesas.zip",
            constant_paths.data_dir / "consolidado",
        )
        df = self.read(
            constant_paths.data_dir / "consolidado" / "consolidado_despesas.csv",
        )
        return df


class ANSApiClient:
    BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/"
    DEMO_CONTABEIS_URL = BASE_URL + "demonstracoes_contabeis/"
    OPERADORAS_ATIVAS_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"

    def __init__(
        self,
        zip_handler: ZipHandler,
        local_storage_client: LocalStorageClient,
    ):
        self.zip_handler = zip_handler
        self.local_storage_client = local_storage_client

    def _find_directories_and_files(self, html_string: str) -> dict[str, list[str]]:
        items: dict[str, list[str]] = {"directories": [], "files": []}
        pattern = r'<a href="([^"]+)"'
        matches: list[str] = re.findall(pattern, html_string)
        for href in matches:
            if href.startswith("/") or href.startswith("?"):
                continue
            if href.startswith(".trashed-"):
                continue

            if href.endswith("/"):
                items["directories"].append(href)
            else:
                items["files"].append(href)

        return items

    def _fetch_zip_file(self, url: str) -> io.BytesIO | None:
        try:
            response = requests.get(url, timeout=30)
            zip_bytes = io.BytesIO(response.content)
            return zip_bytes
        except requests.HTTPError as e:
            print("Error fetching zip file: ", str(e))
            return None

    def download_demo_contabeis(self, limit: int = 3) -> None:
        print("Buscando demonstrações contábeis")
        response = requests.get(self.DEMO_CONTABEIS_URL, timeout=30)
        response.raise_for_status()
        items = self._find_directories_and_files(response.text)
        years = items.get("directories") or []
        if not years:
            raise RuntimeError(f"No directories found in {self.DEMO_CONTABEIS_URL}")

        downloads = 0
        for year in reversed(years):
            if downloads >= limit:
                break

            year_url = f"{self.DEMO_CONTABEIS_URL}{year}/"
            year_response = requests.get(year_url, timeout=30)
            year_response.raise_for_status()

            year_items = self._find_directories_and_files(year_response.text)
            files = year_items.get("files") or []

            for file in reversed(files):
                if downloads >= limit:
                    break

                url = f"{year_url}{file}"
                zip_bytes = self._fetch_zip_file(url)
                if not zip_bytes:
                    break

                files_map = self.zip_handler.extract_files_from_zip_bytes(zip_bytes)
                if files_map:
                    self.local_storage_client.save_files(files_map, constant_paths.trimestres_dir)
                    downloads += 1

    def download_operadoras_ativas(self) -> None:
        print("Buscando operadoras ativas...")
        df = pd.read_csv(self.OPERADORAS_ATIVAS_URL, sep=";", encoding="utf-8", decimal=",")
        df = df[
            ["REGISTRO_OPERADORA", "CNPJ", "Razao_Social", "Modalidade", "UF", "Data_Registro_ANS"]
        ]
        df = df.rename(columns={"REGISTRO_OPERADORA": "REG_ANS"})
        df["REG_ANS"] = df["REG_ANS"].astype(str)
        df["CNPJ"] = df["CNPJ"].astype(str)
        df["Data_Registro_ANS"] = pd.to_datetime(df["Data_Registro_ANS"], errors="coerce")

        # Ordena por data decrescente para que o primeiro registro seja o mais recente
        df = df.sort_values("Data_Registro_ANS", ascending=False)
        df = df.drop_duplicates(subset=["REG_ANS"], keep="first")
        df = df.drop_duplicates(subset=["CNPJ"], keep="first")
        df = df.drop(columns=["Data_Registro_ANS"])

        self.local_storage_client.save_csv_from_df(
            df, constant_paths.operadoras_dir, "operadoras.csv"
        )

    def run(self) -> None:
        self.download_demo_contabeis()
        self.download_operadoras_ativas()
