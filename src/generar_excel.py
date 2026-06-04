import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


_EXCEL_MAX_COLS = 200


def _cargar_dataset(base_name):

    parquet_path = Path(f"data/raw/{base_name}.parquet")
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)

    csv_path = Path(f"data/raw/{base_name}.csv")
    if csv_path.exists():
        return pd.read_csv(csv_path, encoding="utf-8-sig", low_memory=False)

    raise FileNotFoundError(f"No se encuentra {base_name}.parquet ni {base_name}.csv")


def _parquet_to_excel(base_name, out_path, sheet_name="Datos"):

    df = _cargar_dataset(base_name)
    df.to_excel(out_path, index=False, sheet_name=sheet_name)
    logger.info("Excel generado: %s (%s filas × %s cols)", out_path, *df.shape)

    return df


def _parquet_to_excel_split(base_name, out_path, sheet_prefix="Datos"):

    df = _cargar_dataset(base_name)
    ncols = len(df.columns)

    logger.info("  %s: %s filas × %s columnas", base_name, *df.shape)

    if ncols <= _EXCEL_MAX_COLS:
        df.to_excel(out_path, index=False, sheet_name=sheet_prefix)
        logger.info("  -> %s", out_path)
        return df

    chunks = []
    chunk_idx = 1
    for start in range(0, ncols, _EXCEL_MAX_COLS):
        end = min(start + _EXCEL_MAX_COLS, ncols)
        chunk = df.iloc[:, [0] + list(range(start, end))]
        sheet = f"{sheet_prefix}_{chunk_idx}"
        chunks.append((chunk, sheet))
        chunk_idx += 1

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for chunk, sheet in chunks:
            chunk.to_excel(writer, index=False, sheet_name=sheet[:31])

    logger.info("  -> %s (%s sheets)", out_path, len(chunks))

    return df


def generar_excel_revision():

    logger.info("=== GENERANDO EXCEL PARA REVISIÓN ===")

    _parquet_to_excel("cancelados", "data/raw/cancelados.xlsx")
    _parquet_to_excel("inasistencias_agregado", "data/raw/inasistencias_agregado.xlsx")
    _parquet_to_excel("inasistencias_detalle", "data/raw/inasistencias_detalle.xlsx")

    _parquet_to_excel_split("notas_pivot", "data/raw/notas_pivot.xlsx", sheet_prefix="Notas")

    logger.info("=== EXCEL GENERADOS ===")
