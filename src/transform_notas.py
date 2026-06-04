import logging

import pandas as pd

from .utils import guardar_csv, guardar_parquet

logger = logging.getLogger(__name__)


def _es_hoja(parametro, padres):
    return parametro["Consecutivo_parametro"] not in padres


def _extraer_parametros_hoja(parametros_raw):
    if not parametros_raw or not isinstance(parametros_raw, list):
        return {}

    padres = {
        p["Consecutivo_padre"]
        for p in parametros_raw
        if p.get("Consecutivo_padre") is not None
    }

    hojas = [p for p in parametros_raw if _es_hoja(p, padres)]

    return {h["Nombre_parametro"]: h.get("Nota") for h in hojas}


def transformar_notas(df_raw):

    logger.info("=== TRANSFORMANDO NOTAS (pivot de parámetros hoja) ===")

    registros_pivot = []
    todos_param_cols = set()

    filas_temp = []

    for _, row in df_raw.iterrows():
        params_hoja = _extraer_parametros_hoja(row.get("Parametros_evaluacion"))

        fila = row.drop("Parametros_evaluacion").to_dict()
        fila.update(params_hoja)
        filas_temp.append(fila)
        todos_param_cols.update(params_hoja.keys())

    df_pivot = pd.DataFrame(filas_temp)

    logger.info("Columnas de parámetros hoja detectadas: %s", len(todos_param_cols))

    guardar_parquet(df_pivot, "notas_pivot.parquet")
    guardar_csv(df_pivot, "notas_pivot.csv")

    logger.info("Notas pivot guardadas: %s filas × %s columnas", *df_pivot.shape)

    return df_pivot
