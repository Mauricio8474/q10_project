import logging

import pandas as pd

from .utils import guardar_csv, guardar_parquet

logger = logging.getLogger(__name__)


def _extraer_seguimientos(parametros_raw):
    if not parametros_raw or not isinstance(parametros_raw, list):
        return {}

    primeros = parametros_raw[:3]
    etiquetas = ["Primer Seguimiento", "Segundo Seguimiento", "Tercer Seguimiento"]
    return {etiquetas[i]: p.get("Nota") for i, p in enumerate(primeros)}


def transformar_notas(df_raw):

    logger.info("=== TRANSFORMANDO NOTAS (pivot de seguimientos) ===")

    filas_temp = []

    for _, row in df_raw.iterrows():
        seg = _extraer_seguimientos(row.get("Parametros_evaluacion"))

        fila = row.drop("Parametros_evaluacion").to_dict()
        fila.update(seg)
        filas_temp.append(fila)

    df_pivot = pd.DataFrame(filas_temp)

    guardar_parquet(df_pivot, "notas_pivot.parquet")
    guardar_csv(df_pivot, "notas_pivot.csv")

    logger.info("Notas pivot guardadas: %s filas × %s columnas", *df_pivot.shape)

    return df_pivot
