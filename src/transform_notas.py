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
    nombre = str(nombre)
    prefijo = str(codigo) + "-"
    if nombre.startswith(prefijo):
        return nombre[len(prefijo):]
    return nombre


def _calcular_nota_final(row):
    p1 = row.get("Primer Seguimiento") or 0
    p2 = row.get("Segundo Seguimiento") or 0
    p3 = row.get("Tercer Seguimiento") or 0
    return p1 * 0.3 + p2 * 0.3 + p3 * 0.4


def transformar_notas(df_raw):

    logger.info("=== TRANSFORMANDO NOTAS (pivot de seguimientos) ===")

    filas_temp = []

    for _, row in df_raw.iterrows():
        seg = _extraer_seguimientos(row.get("Parametros_evaluacion"))

        fila = row.drop("Parametros_evaluacion").to_dict()
        fila.update(seg)
        filas_temp.append(fila)

    df_pivot = pd.DataFrame(filas_temp)

    df_pivot["Grupo"] = df_pivot["Nombre_curso"].apply(_asignar_grupo)
    df_pivot["Nota final"] = df_pivot.apply(_calcular_nota_final, axis=1)
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
