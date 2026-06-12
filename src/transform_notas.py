import logging
import re

import pandas as pd

from .config import EXCLUIR_PROGRAMAS
from .utils import guardar_csv, guardar_parquet

logger = logging.getLogger(__name__)


def _extraer_seguimientos(parametros_raw):
    if not parametros_raw or not isinstance(parametros_raw, list):
        return {}

    padres = [p for p in parametros_raw if p.get("Consecutivo_padre") is None]
    primeros = padres[:3]
    etiquetas = ["Primer Seguimiento", "Segundo Seguimiento", "Tercer Seguimiento"]
    return {etiquetas[i]: p.get("Nota") for i, p in enumerate(primeros)}


def _asignar_grupo(nombre_curso):
    m = re.search(r"\((\w+)\)\s*$", str(nombre_curso))
    return m.group(1) if m else "A"


def _limpiar_nombre_asignatura(nombre, codigo):
    if pd.isna(nombre) or pd.isna(codigo):
        return nombre
    nombre_str = str(nombre)
    prefijo = str(codigo) + "-"
    return nombre_str[len(prefijo):] if nombre_str.startswith(prefijo) else nombre


def _calcular_nota_final(row):
    return (
        (row.get("Primer Seguimiento") or 0) * 0.3
        + (row.get("Segundo Seguimiento") or 0) * 0.3
        + (row.get("Tercer Seguimiento") or 0) * 0.4
    )


def transformar_notas(df_raw):

    logger.info("=== TRANSFORMANDO NOTAS (pivot de seguimientos) ===")

    df_pivot = df_raw.copy()

    seguimientos = df_pivot["Parametros_evaluacion"].apply(_extraer_seguimientos)
    df_pivot = pd.concat(
        [df_pivot.drop(columns=["Parametros_evaluacion"]), seguimientos.apply(pd.Series)],
        axis=1,
    )

    df_pivot["Grupo"] = df_pivot["Nombre_curso"].apply(_asignar_grupo)
    cols_seg = ["Primer Seguimiento", "Segundo Seguimiento", "Tercer Seguimiento"]
    df_pivot["Nota final"] = (
        df_pivot[cols_seg].fillna(0).mul([0.3, 0.3, 0.4]).sum(axis=1)
    )
    df_pivot["Nombre_asignatura"] = df_pivot.apply(
        lambda r: _limpiar_nombre_asignatura(r["Nombre_asignatura"], r["Codigo_asignatura"]), axis=1
    )

    antes = len(df_pivot)
    df_pivot = df_pivot[~df_pivot["Codigo_programa"].isin(EXCLUIR_PROGRAMAS)].copy()
    logger.info("Programas excluidos: %s registros eliminados", antes - len(df_pivot))

    guardar_parquet(df_pivot, "notas_pivot.parquet")
    guardar_csv(df_pivot, "notas_pivot.csv")

    logger.info("Notas pivot guardadas: %s filas × %s columnas", *df_pivot.shape)

    return df_pivot
