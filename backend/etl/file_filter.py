from pathlib import Path

import pandas as pd

COLUMN_MAPPINGS: dict[str, list[str]] = {
    "REG_ANS": ["REG_ANS", "REGISTRO_ANS", "CD_OPERADORA", "OPERADORA"],
    "CD_CONTA_CONTABIL": ["CD_CONTA_CONTABIL", "CONTA_CONTABIL", "COD_CONTA", "CONTA"],
    "DESCRICAO": ["DESCRICAO", "DESC_CONTA", "NOME_CONTA", "DS_CONTA"],
    "VL_SALDO_FINAL": ["VL_SALDO_FINAL", "SALDO_FINAL", "VL_FINAL", "VALOR_FINAL"],
    "DATA": ["DATA", "DT_BALANCETE", "DATA_BALANCETE", "DT_BASE"],
}


class FileReader:
    SUPPORTED_EXTENSIONS = {".csv", ".txt", ".xlsx", ".xls"}

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


class DespesasProcessor:
    REQUIRED_COLUMNS = ["REG_ANS", "CD_CONTA_CONTABIL", "DESCRICAO", "VL_SALDO_FINAL", "DATA"]

    def __init__(self, contabil_file_path: Path, operadoras_file_path: Path):
        self.contabil_file_path = contabil_file_path
        self.operadoras_file_path = operadoras_file_path
        self.file_reader = FileReader()
        self.column_normalizer = ColumnNormalizer(COLUMN_MAPPINGS)

    def read_file(self, file_path: Path) -> pd.DataFrame:
        df = self.file_reader.read(file_path)
        df = self.column_normalizer.normalize_column_names(df)
        return df

    def filter_despesas(self, df: pd.DataFrame) -> pd.DataFrame:
        # Valida colunas obrigatórias
        missing = self.column_normalizer.validate_required_columns(df, self.REQUIRED_COLUMNS)
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

        print("Filtrando por despesas de evento/sinistro...")
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
        """Enriquece despesas com dados cadastrais das operadoras."""
        df_operadoras["CNPJ"] = df_operadoras["CNPJ"].astype(str)
        df_operadoras["REGISTRO_OPERADORA"] = df_operadoras["REGISTRO_OPERADORA"].astype(str)
        df_despesas["REG_ANS"] = df_despesas["REG_ANS"].astype(str)

        df_operadoras = df_operadoras.rename(columns={"REGISTRO_OPERADORA": "REG_ANS"})

        df_final = df_despesas.merge(
            df_operadoras,
            on="REG_ANS",
            how="left",
        )

        # Remove registros sem match no cadastro (operadoras inativas/canceladas)
        sem_cadastro = df_final["CNPJ"].isna() | (df_final["CNPJ"] == "")
        qtd_sem_cadastro = sem_cadastro.sum()

        if qtd_sem_cadastro > 0:
            df_final = df_final[~sem_cadastro]
            print(f"{qtd_sem_cadastro} registros removidos (REG_ANS sem cadastro ativo)")

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
    supported_patterns = ["*.csv", "*.txt", "*.xlsx", "*.xls"]
    data_files: list[Path] = []

    for pattern in supported_patterns:
        data_files.extend(trimestres_dir.glob(pattern))

    if not data_files:
        raise FileNotFoundError(f"Nenhum arquivo de dados encontrado em {trimestres_dir}")

    print(f"Encontrados {len(data_files)} arquivos para processar")

    consolidated_df = pd.DataFrame()
    processed = 0
    skipped = 0

    for data_file in data_files:
        try:
            processor = DespesasProcessor(data_file, operadoras_file)
            quarter_expenses = processor.run()
            consolidated_df = pd.concat([consolidated_df, quarter_expenses], ignore_index=True)
            processed += 1
        except ValueError as e:
            print(f"Arquivo ignorado ({data_file.name}): {e}")
            skipped += 1

    print(f"Processamento concluído: {processed} arquivos, {skipped} ignorados")
    return consolidated_df
