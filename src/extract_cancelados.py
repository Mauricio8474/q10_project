import logging

import requests
import pandas as pd
import time

from .config import (
    BASE_URL,
    HEADERS,
    PERIODOS,
    PROGRAMAS
)
from .utils import request_with_retry

logger = logging.getLogger(__name__)

# ---------------------------------------------------
# EXTRACCIÓN
# ---------------------------------------------------

def obtener_cancelados(periodo, programa):

    offset = 0
    limit = 5000

    todos = []

    while True:

        params = {
            "Consecutivo_periodo": periodo,
            "Codigo_programa": programa,
            "Limit": limit,
            "Offset": offset
        }

        response = request_with_retry(
            requests.get,
            f"{BASE_URL}/matriculas-canceladas",
            headers=HEADERS,
            params=params
        )

        logger.info(
            "Periodo %s | Programa %s | Offset %s | Status %s",
            periodo, programa, offset, response.status_code
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

# ---------------------------------------------------
# EJECUCIÓN GENERAL
# ---------------------------------------------------

def ejecutar_extraccion():

    registros = []

    for periodo in PERIODOS:

        logger.info("===== PERIODO %s =====", periodo)

        for programa in PROGRAMAS:

            datos = obtener_cancelados(
                periodo,
                programa
            )

            registros.extend(datos)

    df = pd.DataFrame(registros)

    return df