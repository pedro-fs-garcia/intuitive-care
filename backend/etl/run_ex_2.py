from .aggregator import DespesasAggregator
from .clients import LocalStorageClient
from .constants import constant_paths
from .libs import ZipHandler


def run_ex_2() -> None:
    zip_handler = ZipHandler()
    local_storage_client = LocalStorageClient(zip_handler)
    aggregator = DespesasAggregator(local_storage_client)

    df_agregado = aggregator.run()

    local_storage_client.save_csv_from_df(
        df_agregado, constant_paths.output_dir, "despesas_agregadas.csv"
    )

    # local_storage_client.save_zip_csv_from_df(
    #     df_agregado,
    #     constant_paths.output_dir,
    #     "Teste_pedro_garcia.zip",
    #     "despesas_agregadas.csv"
    # )


if __name__ == "__main__":
    run_ex_2()
