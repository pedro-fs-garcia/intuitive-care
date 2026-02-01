from pathlib import Path


class ConstantPaths:
    _base_dir = Path(__file__).resolve().parent
    root_dir = _base_dir.parents[1]
    data_dir = root_dir / "data"
    output_dir = root_dir / "output"
    operadoras_dir = data_dir / "operadoras"
    trimestres_dir = data_dir / "trimestres"


constant_paths = ConstantPaths()
