import logging
from pathlib import Path

import pandas as pd
import requests
import time

from .config import BASE_URL, HEADERS, PERIODOS, EXCLUIR_PROGRAMAS
from .utils import request_with_retry, guardar_parquet, guardar_csv

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

        if response is None:
            logger.warning("Estudiantes periodo %s | Offset %s | Sin respuesta — abortando", periodo, offset)
            break

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


def _actualizar_nivel_en_notas(df_estudiantes):

    ruta = Path("data/raw/notas_pivot.parquet")
    if not ruta.exists():
        logger.warning("notas_pivot.parquet no encontrado, se omite actualización de Nombre_nivel")
        return

    notas = pd.read_parquet(ruta)

    nivel_por_id = (
        df_estudiantes[["Numero_identificacion", "Nombre_nivel"]]
        .dropna(subset=["Numero_identificacion"])
        .drop_duplicates(subset="Numero_identificacion", keep="last")
        .rename(columns={"Numero_identificacion": "Numero_identificacion_estudiante"})
    )

    antes = len(notas)
    if "Nombre_nivel" in notas.columns:
        notas = notas.drop(columns=["Nombre_nivel"])
    notas = notas.merge(nivel_por_id, on="Numero_identificacion_estudiante", how="left")
    assert len(notas) == antes, "El merge de Nombre_nivel no debe alterar el número de filas"

    guardar_parquet(notas, "notas_pivot.parquet")
    guardar_csv(notas, "notas_pivot.csv")
    logger.info("Nombre_nivel agregado a notas_pivot desde estudiantes")


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
        if "Calendario" in notas.columns:
            cal_por_id = (
                notas[["Numero_identificacion_estudiante", "Calendario"]]
                .drop_duplicates()
                .groupby("Numero_identificacion_estudiante")["Calendario"]
                .apply(lambda x: ", ".join(sorted(x.unique().astype(str))))
                .reset_index()
                .rename(columns={"Numero_identificacion_estudiante": "Numero_identificacion"})
            )
            df = df.merge(cal_por_id, on="Numero_identificacion", how="left")
            logger.info("Calendario agregado desde notas_pivot")
    except FileNotFoundError:
        logger.warning("notas_pivot.parquet no encontrado, se omite Grupo")

    try:
        cancelados = pd.read_parquet("data/raw/cancelados.parquet")
        ids_cancelados = set(cancelados["Numero_identificacion"].unique())
        df["Estado"] = df["Numero_identificacion"].apply(
            lambda x: "Cancelado" if x in ids_cancelados else "Activo"
        )
        logger.info(
            "Estado agregado: %s activos, %s cancelados",
            (df["Estado"] == "Activo").sum(),
            (df["Estado"] == "Cancelado").sum(),
        )
    except FileNotFoundError:
        logger.warning("cancelados.parquet no encontrado, se omite Estado")
        df["Estado"] = "Activo"

    antes = len(df)
    df = df[~df["Codigo_programa"].isin(EXCLUIR_PROGRAMAS)].copy()
    logger.info("Programas excluidos: %s registros eliminados", antes - len(df))

    guardar_parquet(df, "estudiantes.parquet")
    try:
        df.to_csv("data/raw/estudiantes.csv", index=False, encoding="utf-8-sig")
        logger.info("CSV guardado: data/raw/estudiantes.csv")
    except PermissionError:
        logger.warning("No se pudo guardar estudiantes.csv (archivo abierto en otro programa)")

    logger.info("Estudiantes guardados: %s registros", len(df))

    _actualizar_nivel_en_notas(df)

    return df
