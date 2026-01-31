from pathlib import Path

import pandas as pd


class ExpenseProcessor:
    def __init__(self, contabil_file_path: Path, operadoras_file_path: Path):
        self.contabil_file_path = contabil_file_path
        self.operadoras_file_path = operadoras_file_path
        return

    def read_file(self, file_path: Path) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path, sep=";", encoding="utf-8", decimal=",")
            print("Formato utf-8")
            print(f"linhas: {len(df)}")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, sep=";", encoding="latin1", decimal=",")
            print("Formato latin1")
        return df

    def filter_despesas(self, df: pd.DataFrame) -> pd.DataFrame:
        print("Filtrando por despesas de evento/sinistro")
        df["CD_CONTA_CONTABIL"] = df["CD_CONTA_CONTABIL"].astype(str)
        df_despesas = df[
            (df["CD_CONTA_CONTABIL"].str.startswith("4"))
            & (df["DESCRICAO"].str.contains("EVENTO|SINISTRO", case=False, na=False))
        ].copy()

        df_despesas["VL_SALDO_FINAL"] = (
            df_despesas["VL_SALDO_FINAL"].astype(str).str.replace(",", ".", regex=False)
        )

        df_despesas["VL_SALDO_FINAL"] = pd.to_numeric(
            df_despesas["VL_SALDO_FINAL"], errors="coerce"
        ).fillna(0)
        df_despesas["DATA"] = pd.to_datetime(df_despesas["DATA"], errors="coerce")
        df_despesas = df_despesas.dropna(subset=["DATA"])
        df_despesas["Ano"] = df_despesas["DATA"].dt.year
        df_despesas["Trimestre"] = df_despesas["DATA"].dt.quarter
        df_despesas = (
            df_despesas.groupby(["REG_ANS", "Ano", "Trimestre"])["VL_SALDO_FINAL"]
            .sum()
            .reset_index()
        )
        df_despesas = df_despesas[["Ano", "Trimestre", "REG_ANS", "VL_SALDO_FINAL"]]
        print(f"linhas finais: {len(df_despesas)}")
        return df_despesas

    def join_operadoras(
        self, df_despesas: pd.DataFrame, df_operadoras: pd.DataFrame
    ) -> pd.DataFrame:
        print(df_despesas)
        print(df_operadoras)
        df_operadoras["CNPJ"] = df_operadoras["CNPJ"].astype(str)
        df_operadoras["REGISTRO_OPERADORA"] = df_operadoras["REGISTRO_OPERADORA"].astype(str)
        df_despesas["REG_ANS"] = df_despesas["REG_ANS"].astype(str)

        df_operadoras = df_operadoras.rename(columns={"REGISTRO_OPERADORA": "REG_ANS"})

        df_final = df_despesas.merge(
            df_operadoras,
            on="REG_ANS",
            how="left",
        )

        df_final = df_final[["CNPJ", "Razao_Social", "Trimestre", "Ano", "VL_SALDO_FINAL"]]
        df_final = df_final.rename(
            columns={"Razao_Social": "RazaoSocial", "VL_SALDO_FINAL": "ValorDespesas"}
        )
        return df_final

    def export_to_csv(self, df: pd.DataFrame, csv_name: str) -> None:
        df.to_csv(
            csv_name,
            index=False,
            sep=";",
            decimal=",",
            encoding="utf-8",
        )

    def run(self) -> pd.DataFrame:
        df_contabil = self.read_file(self.contabil_file_path)
        df_despesas = self.filter_despesas(df_contabil)
        df_operadoras = self.read_file(self.operadoras_file_path)
        df_consolidated = self.join_operadoras(df_despesas, df_operadoras)
        return df_consolidated


def consolidate_despesas(trimestres_dir: Path, operadoras_file: Path) -> pd.DataFrame:
    csv_files = list(trimestres_dir.glob("*.csv"))

    consolidated_df = pd.DataFrame()

    for csv_file in csv_files:
        processor = ExpenseProcessor(csv_file, operadoras_file)
        quarter_expenses = processor.run()
        consolidated_df = pd.concat([consolidated_df, quarter_expenses], ignore_index=True)

    return consolidated_df
