from .clients import ANSApiClient, LocalStorageClient
from .consolidator import DespesasConsolidator
from .constants import constant_paths
from .libs import ZipHandler, column_normalizer


def run_ex1() -> None:
    zip_handler = ZipHandler()
    local_storage_client = LocalStorageClient(zip_handler)
    ans_api_client = ANSApiClient(zip_handler, local_storage_client)

    ans_api_client.run()

    consolidator = DespesasConsolidator(local_storage_client, column_normalizer)
    df = consolidator.run_batch()
    local_storage_client.save_zip_csv_from_df(
        df, constant_paths.output_dir, "consolidado_despesas.zip", "consolidado_despesas.csv"
    )


if __name__ == "__main__":
    run_ex1()
