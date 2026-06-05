import logging

import pandas as pd
import requests
import time

from .config import BASE_URL, HEADERS, PERIODOS
from .utils import request_with_retry, guardar_parquet

logger = logging.getLogger(__name__)


def separar_sede_programa(nombre):
    partes = nombre.split(" - ")
    sede = partes[0].strip()
    programa = partes[-1].strip()
    return sede, programa


def obtener_estudiantes(periodo, limit=5000):

    offset = 0
    todos = []

    while True:
        params = {
            "Periodo": periodo,
            "Limit": limit,
            "Offset": offset
        }

        response = request_with_retry(
            requests.get,
            f"{BASE_URL}/estudiantes",
            headers=HEADERS,
            params=params
        )

        logger.info(
            "Estudiantes periodo %s | Offset %s | Status %s",
            periodo, offset, response.status_code
        )

        if response.status_code != 200:
            break

        data = response.json()

        if not data:
            break

        todos.extend(data)

        if len(data) < limit:
            break

        offset += limit
        time.sleep(0.2)

    return todos


def ejecutar_extraccion_estudiantes():

    logger.info("=== EXTRAYENDO ESTUDIANTES (clasificación) ===")

    registros = []

    for periodo in PERIODOS:
        logger.info("Periodo %s", periodo)
        data = obtener_estudiantes(periodo)
        registros.extend(data)
        logger.info("  Periodo %s: %s estudiantes", periodo, len(data))

    df = pd.DataFrame(registros)

    if "Nombre_programa" in df.columns:
        df[["Sede", "Nombre_programa_limpio"]] = df["Nombre_programa"].apply(
            lambda x: pd.Series(separar_sede_programa(x))
        )

    try:
        notas = pd.read_parquet("data/raw/notas_pivot.parquet")
        grupo_por_id = (
            notas[["Numero_identificacion_estudiante", "Grupo"]]
            .drop_duplicates()
            .groupby("Numero_identificacion_estudiante")["Grupo"]
            .apply(lambda x: ", ".join(sorted(x.unique())))
            .reset_index()
            .rename(columns={"Numero_identificacion_estudiante": "Numero_identificacion"})
        )
        df = df.merge(grupo_por_id, on="Numero_identificacion", how="left")
        logger.info("Grupo agregado desde notas_pivot")
    except FileNotFoundError:
        logger.warning("notas_pivot.parquet no encontrado, se omite Grupo")

    guardar_parquet(df, "estudiantes.parquet")
    try:
        df.to_csv("data/raw/estudiantes.csv", index=False, encoding="utf-8-sig")
        logger.info("CSV guardado: data/raw/estudiantes.csv")
    except PermissionError:
        logger.warning("No se pudo guardar estudiantes.csv (archivo abierto en otro programa)")

    logger.info("Estudiantes guardados: %s registros", len(df))

    return df
