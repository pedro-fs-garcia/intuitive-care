import os
import zipfile as zf
from io import BytesIO
from pathlib import Path

from pandas import DataFrame


class ZipHandler:
    def _safe_extract(self, zip_file: zf.ZipFile, path: Path) -> None:
        for member in zip_file.namelist():
            final_path = os.path.abspath(os.path.join(path, member))
            if not final_path.startswith(os.path.abspath(path)):
                raise RuntimeError("Zip malicioso detectado")
        zip_file.extractall(path)

    def extract_quarters(self, zip_bytes: BytesIO, output_dir: Path) -> None:
        with zf.ZipFile(zip_bytes) as zip_file:
            self._safe_extract(zip_file, output_dir)

    def export_df_to_zip(
        self, df: DataFrame, output_path: Path, zip_name: str, csv_name: str
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
