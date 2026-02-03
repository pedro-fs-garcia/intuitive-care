import pandas as pd

from .clients import LocalStorageClient
from .constants import constant_paths
from .libs import normalize_cnpj


class DespesasAggregator:
    def __init__(self, local_storage_client: LocalStorageClient) -> None:
        self.local_storage_client = local_storage_client

    def _load_consolidate_df(self) -> pd.DataFrame:
        df = self.local_storage_client.extract_despesas_consolidate_df()
        return df

    def _clean_consolidate_df(self, df: pd.DataFrame) -> pd.DataFrame:
        df["CNPJ"] = df["CNPJ"].astype(str)
        df["CNPJ"] = df["CNPJ"].apply(lambda x: normalize_cnpj(str(x)) if pd.notna(x) else None)
        df["ValorDespesas"] = pd.to_numeric(df["ValorDespesas"], errors="coerce")
        df = df[
            df["CNPJ"].notna()
            & (df["ValorDespesas"] > 0)
            & df["RazaoSocial"].notna()
            & df["RazaoSocial"].str.strip().ne("")
        ]
        return df

    def join_operadoras(
        self, df_consolidate: pd.DataFrame, df_operadoras: pd.DataFrame
    ) -> pd.DataFrame:
        df_operadoras = df_operadoras.rename(columns={"REG_ANS": "RegistroANS"})
        df_operadoras = df_operadoras.drop_duplicates(subset=["RegistroANS"], keep="first")
        df_operadoras = df_operadoras.drop_duplicates(subset=["CNPJ"], keep="first")
        df_operadoras["CNPJ"] = df_operadoras["CNPJ"].astype(str).str.zfill(14)

        df_merge = df_consolidate.merge(
            df_operadoras,
            on="CNPJ",
            how="inner",
        )

        keep_cols = [
            "CNPJ",
            "RazaoSocial",
            "Trimestre",
            "Ano",
            "ValorDespesas",
            "RegistroANS",
            "Modalidade",
            "UF",
        ]
        df_merge = df_merge[keep_cols]

        return df_merge

    def aggregate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrupa dados por operadora e UF com métricas estatísticas."""
        df = df.sort_values(["CNPJ", "Ano", "Trimestre"])
        df["DespesaTrimestre"] = (
            df.groupby(["CNPJ", "Ano"])["ValorDespesas"].diff().fillna(df["ValorDespesas"])
        )
        df_agg = (
            df.groupby(["CNPJ", "RegistroANS", "RazaoSocial", "Modalidade", "UF"])
            .agg(
                TotalDespesas=("DespesaTrimestre", "sum"),
                MediaTrimestral=("DespesaTrimestre", "mean"),
                DesvioPadrao=("DespesaTrimestre", "std"),
                QtdTrimestres=("ValorDespesas", "count"),
            )
            .reset_index()
        )
        df_agg["DesvioPadrao"] = df_agg["DesvioPadrao"].fillna(0)
        df_agg[["TotalDespesas", "MediaTrimestral", "DesvioPadrao"]] = df_agg[
            ["TotalDespesas", "MediaTrimestral", "DesvioPadrao"]
        ].round(2)
        df_agg = df_agg.sort_values("TotalDespesas", ascending=False)
        return df_agg

    def run(self) -> pd.DataFrame:
        df_consolidate = self._load_consolidate_df()
        df_consolidate = self._clean_consolidate_df(df_consolidate)

        df_operadoras = self.local_storage_client.read(
            constant_paths.operadoras_dir / "operadoras.csv"
        )

        df = self.join_operadoras(df_consolidate, df_operadoras)
        df = self.aggregate(df)
        return df
