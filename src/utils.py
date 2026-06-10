import logging
import time
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests

# ---------------------------------------------------
# LOGGING
# ---------------------------------------------------

def setup_logging(nivel=logging.INFO):
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

# ---------------------------------------------------
# REINTENTOS EN PETICIONES HTTP
# ---------------------------------------------------

def request_with_retry(func, *args, max_retries=3, delay=1, **kwargs):
    for intento in range(max_retries):
        try:
            response = func(*args, timeout=30, **kwargs)
            if response.status_code in (429, 502, 503, 504):
                logger.warning(
                    "Status %s — reintento %s/%s",
                    response.status_code, intento + 1, max_retries
                )
                time.sleep(delay * (2 ** intento))
                continue
            return response
        except (requests.ConnectionError, requests.Timeout) as e:
            logger.warning(
                "Error de conexión: %s — reintento %s/%s",
                e, intento + 1, max_retries
            )
            time.sleep(delay * (2 ** intento))
    logger.error(
        "Fallaron los %s intentos para %s — devolviendo None",
        max_retries, func.__name__
    )
    return None

logger = logging.getLogger(__name__)

# ---------------------------------------------------
# CREAR DIRECTORIOS
# ---------------------------------------------------

def crear_directorios():

    rutas = [
        "data",
        "data/raw",
        "data/processed",
        "logs"
    ]

    for ruta in rutas:
        Path(ruta).mkdir(
            parents=True,
            exist_ok=True
        )

# ---------------------------------------------------
# GUARDAR CSV
# ---------------------------------------------------

def guardar_csv(df, nombre_archivo):

    Path("data/raw").mkdir(parents=True, exist_ok=True)

    ruta = f"data/raw/{nombre_archivo}"

    df.to_csv(
        ruta,
        index=False,
        encoding="utf-8-sig"
    )

    logger.info("CSV guardado en: %s", ruta)

# ---------------------------------------------------
# GUARDAR PARQUET
# ---------------------------------------------------

def guardar_parquet(df, nombre_archivo):

    Path("data/raw").mkdir(parents=True, exist_ok=True)

    ruta = f"data/raw/{nombre_archivo}"

    df.to_parquet(ruta, index=False)

    logger.info("Parquet guardado en: %s", ruta)

# ---------------------------------------------------
# LIMPIAR COLUMNAS
# ---------------------------------------------------

def limpiar_columnas(df):

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df

# ---------------------------------------------------
# RESUMEN DATAFRAME
# ---------------------------------------------------

def resumen_dataframe(df):

    logger.info("=== RESUMEN DATAFRAME ===")
    logger.info("Filas: %s | Columnas: %s", df.shape[0], df.shape[1])
    logger.info("Columnas: %s", df.columns.tolist())

# ---------------------------------------------------
# FECHA ACTUAL
# ---------------------------------------------------

def fecha_actual():

    return datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )