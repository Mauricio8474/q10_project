import logging

import pandas as pd
import requests
import time

from .config import BASE_URL, HEADERS
from .utils import request_with_retry, guardar_parquet

logger = logging.getLogger(__name__)


def obtener_cursos(limit=5000):

    offset = 0
    todos = []

    while True:
        params = {
            "Limit": limit,
            "Offset": offset,
            "Estado": "Abierto"
        }

        response = request_with_retry(
            requests.get,
            f"{BASE_URL}/cursos",
            headers=HEADERS,
            params=params
        )

        if response is None:
            logger.warning("Cursos | Offset %s | Sin respuesta — abortando", offset)
            break

        logger.info("Cursos | Offset %s | Status %s", offset, response.status_code)

        if response.status_code != 200:
            logger.warning("Cursos | Offset %s | Status %s — abortando", offset, response.status_code)
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


def ejecutar_extraccion_cursos():

    logger.info("=== EXTRAYENDO CURSOS ===")

    raw = obtener_cursos()
    df = pd.DataFrame(raw)

    logger.info("Total cursos extraídos: %s", len(df))

    guardar_parquet(df, "cursos.parquet")
    df.to_csv("data/raw/cursos.csv", index=False, encoding="utf-8-sig")

    logger.info("Cursos guardados en data/raw/cursos.{parquet,csv}")

    return df
