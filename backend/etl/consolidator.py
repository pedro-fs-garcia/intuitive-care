from pathlib import Path

import pandas as pd

from .clients import LocalStorageClient
from .constants import constant_paths
from .libs import ColumnNormalizer


class DespesasConsolidator:
    REQUIRED_COLUMNS = [
        "DATA",
        "REG_ANS",
        "CD_CONTA_CONTABIL",
        "DESCRICAO",
        "VL_SALDO_INICIAL",
        "VL_SALDO_FINAL",
    ]

    def __init__(
        self, local_storage_client: LocalStorageClient, column_normalizer: ColumnNormalizer
    ):
        self.local_storage_client = local_storage_client
        self.column_normalizer = column_normalizer

    def load_despesas_df(self, file_path: Path) -> pd.DataFrame:
        df = self.local_storage_client.read(file_path)
        missing = self.column_normalizer.validate_required_columns(df, self.REQUIRED_COLUMNS)
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

        df["CD_CONTA_CONTABIL"] = df["CD_CONTA_CONTABIL"].astype(str)
        df["VL_SALDO_FINAL"] = df["VL_SALDO_FINAL"].astype(str).str.replace(",", ".", regex=False)
        df["VL_SALDO_FINAL"] = pd.to_numeric(df["VL_SALDO_FINAL"], errors="coerce").fillna(0)
        df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce")
        df = df.dropna(subset=["DATA"])
        return df

    def load_operadoras_df(self) -> pd.DataFrame:
        df = self.local_storage_client.read(constant_paths.operadoras_dir / "operadoras.csv")
        df["CNPJ"] = df["CNPJ"].astype(str).str.zfill(14)
        return df

    def filter_despesas(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Filtrando por despesas de evento/sinistro...")
        df["DESCRICAO"] = df["DESCRICAO"].str.strip().str.upper()
        df_despesas = df[
            (df["CD_CONTA_CONTABIL"].str.startswith("4"))
            & (df["DESCRICAO"] == "DESPESAS COM EVENTOS / SINISTROS")
            & (df["CD_CONTA_CONTABIL"].str.len() == 9)
        ].copy()

        df_despesas["Ano"] = df_despesas["DATA"].dt.year
        df_despesas["Trimestre"] = df_despesas["DATA"].dt.quarter
        df_despesas = (
            df_despesas.groupby(["REG_ANS", "Ano", "Trimestre"])["VL_SALDO_FINAL"]
            .sum()
            .reset_index()
        )
        df_despesas = df_despesas[["Ano", "Trimestre", "REG_ANS", "VL_SALDO_FINAL"]]
        df_despesas[["VL_SALDO_FINAL"]] = df_despesas[["VL_SALDO_FINAL"]].round(2)
        print(f"linhas finais: {len(df_despesas)}")
        return df_despesas

    def join_operadoras(
        self, df_despesas: pd.DataFrame, df_operadoras: pd.DataFrame
    ) -> pd.DataFrame:
        """Enriquece despesas com dados cadastrais das operadoras."""

        df_final = df_despesas.merge(
            df_operadoras,
            on="REG_ANS",
            how="left",
        )
        sem_cadastro = df_final["CNPJ"].isna() | (df_final["CNPJ"] == "")
        qtd_sem_cadastro = sem_cadastro.sum()

        if qtd_sem_cadastro > 0:
            df_final = df_final[~sem_cadastro]
            print(f"{qtd_sem_cadastro} registros removidos (REG_ANS sem cadastro ativo)")

        keep_cols = ["CNPJ", "Razao_Social", "Trimestre", "Ano", "VL_SALDO_FINAL"]
        rename_map = {
            "Razao_Social": "RazaoSocial",
            "VL_SALDO_FINAL": "ValorDespesas",
        }
        df_final = df_final[keep_cols]
        df_final = df_final.rename(columns=rename_map)
        return df_final

    def run_batch(self) -> pd.DataFrame:
        supported_patterns = ["*.csv", "*.txt", "*.xlsx", "*.xls"]
        data_files: list[Path] = []

        for pattern in supported_patterns:
            data_files.extend(constant_paths.trimestres_dir.glob(pattern))

        data_files.sort()
        if not data_files:
            raise FileNotFoundError(
                f"Nenhum arquivo de dados encontrado em {constant_paths.trimestres_dir}"
            )

        print(f"Encontrados {len(data_files)} arquivos para processar")

        df_consolidate = pd.DataFrame()
        df_operadoras = self.load_operadoras_df()
        processed = 0
        skipped = 0
        for data_file in data_files:
            try:
                df_despesas = self.load_despesas_df(data_file)
                df_despesas = self.filter_despesas(df_despesas)
                df_join = self.join_operadoras(df_despesas, df_operadoras)
                df_consolidate = pd.concat([df_consolidate, df_join], ignore_index=True)
                processed += 1
            except ValueError as e:
                print(f"Arquivo ignorado ({data_file.name}): {e}")
                skipped += 1

        print(f"Processamento concluído: {processed} arquivos, {skipped} ignorados")
        return df_consolidate
