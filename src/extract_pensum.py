import logging
import time

import pandas as pd
import requests

from .config import BASE_URL, HEADERS, PROGRAMAS
from .utils import guardar_csv, guardar_parquet, request_with_retry

logger = logging.getLogger(__name__)


def obtener_diseno_curricular(codigo_programa):

    response = request_with_retry(
        requests.get,
        f"{BASE_URL}/cuantitativo-tradicional-peru/disenio-curricular",
        headers=HEADERS,
        params={"Codigo_programa": codigo_programa}
    )

    if response is None:
        logger.warning("Pensum | Programa %s | Sin respuesta — saltando", codigo_programa)
        return None

    logger.info("Pensum | Programa %s | Status %s", codigo_programa, response.status_code)

    if response.status_code != 200:
        logger.warning("Pensum | Programa %s | Status %s — saltando", codigo_programa, response.status_code)
        return None

    return response.json()


def _aplanar_pensum(data):

    if not data:
        return []

    filas = []

    for pensum in data.get("Pensum") or []:

        if not pensum.get("Pensum_actual"):
            continue

        for asignatura in pensum.get("Asignaturas") or []:
            filas.append({
                "Codigo_programa": data.get("Codigo_programa"),
                "Nombre_programa": data.get("Nombre_programa"),
                "Consecutivo_pensum_programa": pensum.get("Consecutivo_pensum_programa"),
                "Nombre_pensum_programa": pensum.get("Nombre_pensum_programa"),
                "Codigo_asignatura": asignatura.get("Codigo_asignatura"),
                "Nombre_asignatura": asignatura.get("Nombre_asignatura"),
                "Abreviacion_asignatura": asignatura.get("Abreviacion_asignatura"),
                "Codigo_nivel": asignatura.get("Codigo_nivel"),
                "Nombre_nivel": asignatura.get("Nombre_nivel"),
                "Intensidad_horaria_semanal": asignatura.get("Intensidad_horaria_semanal"),
                "Intensidad_horaria_total": asignatura.get("Intensidad_horaria_total"),
                "Creditos_asignatura": asignatura.get("Creditos_asignatura"),
            })

    return filas


def ejecutar_extraccion_pensum():

    logger.info("=== EXTRAYENDO PENSUM (créditos por asignatura) ===")

    filas = []

    for programa in PROGRAMAS:
        data = obtener_diseno_curricular(programa)
        filas.extend(_aplanar_pensum(data))
        time.sleep(0.2)

    df = pd.DataFrame(filas)

    guardar_parquet(df, "pensum.parquet")
    guardar_csv(df, "pensum.csv")

    logger.info(
        "Pensum guardado: %s asignaturas de %s programas",
        len(df), df["Codigo_programa"].nunique() if not df.empty else 0
    )

    return df
