import os
import re
import zipfile as zf
from io import BytesIO
from pathlib import Path

import pandas as pd


def normalize_cnpj(cnpj: str | None) -> str | None:
    if cnpj is None:
        return None

    def calculate_digit(slice: str, weights: tuple[int, ...]) -> str:
        s = 0
        for i in range(len(slice)):
            s += int(slice[i]) * weights[i]
        rest = s % 11
        return "0" if rest < 2 else str(11 - rest)

    dv_1_weights = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    dv_2_weights = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
    cnpj = re.sub(r"[^0-9]", "", cnpj)
    cnpj = cnpj.zfill(14)

    if len(cnpj) != 14 or len(set(cnpj)) == 1:
        return None

    dv_1 = calculate_digit(cnpj[:12], dv_1_weights)
    dv_2 = calculate_digit(cnpj[:13], dv_2_weights)

    return cnpj if cnpj[12:] == dv_1 + dv_2 else None


COLUMN_MAPPINGS: dict[str, list[str]] = {
    "REG_ANS": ["REG_ANS", "REGISTRO_ANS", "CD_OPERADORA", "OPERADORA"],
    "CD_CONTA_CONTABIL": ["CD_CONTA_CONTABIL", "CONTA_CONTABIL", "COD_CONTA", "CONTA"],
    "DESCRICAO": ["DESCRICAO", "DESC_CONTA", "NOME_CONTA", "DS_CONTA"],
    "VL_SALDO_FINAL": ["VL_SALDO_FINAL", "SALDO_FINAL", "VL_FINAL", "VALOR_FINAL"],
    "DATA": ["DATA", "DT_BALANCETE", "DATA_BALANCETE", "DT_BASE"],
}


class ColumnNormalizer:
    def __init__(self, mappings: dict[str, list[str]]):
        self.mappings = mappings

    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df_columns_upper = {col.upper(): col for col in df.columns}
        rename_map: dict[str, str] = {}

        for standard_name, variants in self.mappings.items():
            for variant in variants:
                if variant.upper() in df_columns_upper:
                    original_col = df_columns_upper[variant.upper()]
                    if original_col != standard_name:
                        rename_map[original_col] = standard_name
                    break

        if rename_map:
            print(f"Colunas normalizadas: {rename_map}")
            df = df.rename(columns=rename_map)

        return df

    def validate_required_columns(self, df: pd.DataFrame, required: list[str]) -> list[str]:
        return [col for col in required if col not in df.columns]


column_normalizer = ColumnNormalizer(COLUMN_MAPPINGS)


class ZipHandler:
    def _safe_extract(self, zip_file: zf.ZipFile, path: Path) -> None:
        for member in zip_file.namelist():
            final_path = os.path.abspath(os.path.join(path, member))
            if not final_path.startswith(os.path.abspath(path)):
                raise RuntimeError("Zip malicioso detectado")
        zip_file.extractall(path)

    def extract_from_zip_bytes(self, zip_bytes: BytesIO, output_dir: Path) -> None:
        with zf.ZipFile(zip_bytes) as zip_file:
            self._safe_extract(zip_file, output_dir)

    def extract_local_file(self, source_file_path: Path, output_dir: Path) -> None:
        with zf.ZipFile(source_file_path) as zip_file:
            self._safe_extract(zip_file, output_dir)

    def export_df_to_zip(
        self, df: pd.DataFrame, output_path: Path, zip_name: str, csv_name: str
    ) -> None:
        print("Saving csv to zip file")
        df.to_csv(
            output_path / zip_name,
            index=False,
            sep=";",
            decimal=",",
            encoding="utf-8",
            compression={"method": "zip", "archive_name": csv_name},
        )

    def extract_files_from_zip_bytes(self, zip_bytes: BytesIO) -> dict[str, BytesIO]:
        files: dict[str, BytesIO] = {}

        with zf.ZipFile(zip_bytes) as z:
            for info in z.infolist():
                if info.is_dir():
                    continue

                p = Path(info.filename)
                if p.is_absolute() or ".." in p.parts:
                    raise RuntimeError("zip malicioso")

                with z.open(info) as f:
                    files[info.filename] = BytesIO(f.read())

        return files
