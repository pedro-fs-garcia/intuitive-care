import io
import re
from pathlib import Path

import pandas as pd
import requests

from .zip_extractor import ZipHandler


class ANSDownloader:
    BASE_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/"
    DEMO_CONTABEIS_URL = BASE_URL + "demonstracoes_contabeis/"
    OPERADORAS_ATIVAS_URL = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/Relatorio_cadop.csv"

    def __init__(self, zip_extractor: ZipHandler, base_output_dir: Path):
        self.zip_extractor = zip_extractor
        self.base_output_dir = base_output_dir
        self.operadoras_output_dir = self.base_output_dir / "operadoras"
        self.trimestres_output_dir = self.base_output_dir / "trimestres"

        self.operadoras_output_dir.mkdir(parents=True, exist_ok=True)
        self.trimestres_output_dir.mkdir(parents=True, exist_ok=True)

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

    def _fetch_quarters(self, url: str) -> bool:
        try:
            response = requests.get(url, timeout=30)
            zip_bytes = io.BytesIO(response.content)
            self.zip_extractor.extract_quarters(zip_bytes, self.trimestres_output_dir)
            return True
        except requests.HTTPError as e:
            print("Error fetching zip file: ", str(e))
            return False

    def fetch_demo_contabeis(self, limit: int = 3) -> None:
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
                if not self._fetch_quarters(url):
                    break

                downloads += 1

    def fetch_operadoras_ativas(self) -> None:
        print("Buscando operadoras ativas...")
        df = pd.read_csv(self.OPERADORAS_ATIVAS_URL, sep=";", encoding="utf-8", decimal=",")
        df = df[["REGISTRO_OPERADORA", "CNPJ", "Razao_Social"]]
        df.to_csv(
            self.operadoras_output_dir / "operadoras.csv",
            sep=";",
            decimal=",",
            encoding="utf-8",
            index=False,
        )

    def run(self) -> None:
        self.fetch_demo_contabeis()
        self.fetch_operadoras_ativas()
