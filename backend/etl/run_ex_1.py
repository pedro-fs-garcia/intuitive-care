from pathlib import Path

from .ans_downloader import ANSDownloader
from .file_filter import consolidate_despesas
from .zip_extractor import ZipHandler


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    root_dir = base_dir.parents[1]
    data_dir = root_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    zip_handler = ZipHandler()
    downloader = ANSDownloader(zip_handler, data_dir)

    trimestres_dir = downloader.trimestres_output_dir
    operadoras_dir = downloader.operadoras_output_dir

    downloader.run()
    operadoras_file = operadoras_dir / "operadoras.csv"

    consolidated_expenses = consolidate_despesas(trimestres_dir, operadoras_file)

    zip_handler.export_df_to_zip(
        consolidated_expenses,
        root_dir / "output",
        "consolidado_despesas.zip",
        "consolidado_despesas.csv",
    )


if __name__ == "__main__":
    main()
