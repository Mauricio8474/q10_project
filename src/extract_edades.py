import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests
import time
from datetime import date
from .config import BASE_URL, HEADERS
from .utils import request_with_retry

logger = logging.getLogger(__name__)


# ---------------------------------------------------
# CONSULTA INDIVIDUAL POR ESTUDIANTE
# ---------------------------------------------------

def obtener_datos_estudiante(codigo_estudiante: str, codigo_programa: str = None) -> dict:
    url = f"{BASE_URL}/estudiantes/{codigo_estudiante}"
    params = {}
    if codigo_programa:
        params["Codigo_programa"] = codigo_programa

    try:
        response = request_with_retry(
            requests.get, url,
            headers=HEADERS, params=params
        )
        if response is None:
            logger.warning("Sin respuesta para estudiante %s", codigo_estudiante)
            return {}
        if response.status_code != 200:
            logger.warning("Status %s para estudiante %s", response.status_code, codigo_estudiante)
            return {}
        return response.json()
    except (requests.RequestException, ValueError, TypeError, KeyError) as e:
        logger.error("Error al consultar estudiante %s: %s", codigo_estudiante, e)
        return {}


# ---------------------------------------------------
# CÁLCULO DE EDAD
# ---------------------------------------------------

def calcular_edad(fecha_nacimiento_str: str) -> int | None:
    """
    Calcula la edad en años a partir de una fecha en formato 'YYYY-MM-DD'
    o 'YYYY-MM-DDTHH:MM:SSZ'. Retorna None si no se puede parsear.
    """
    if not fecha_nacimiento_str:
        return None

    try:
        # Normalizar: tomar solo la parte de la fecha
        fecha_str = fecha_nacimiento_str[:10]
        nacimiento = date.fromisoformat(fecha_str)
        hoy = date.today()

        edad = hoy.year - nacimiento.year - (
            (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day)
        )
        return edad

    except (ValueError, TypeError):
        return None


# ---------------------------------------------------
# ENRIQUECIMIENTO DEL DATAFRAME
# ---------------------------------------------------

def _fetch_estudiante(codigo, programa, cache):
    if codigo in cache:
        return cache[codigo]
    datos = obtener_datos_estudiante(codigo, programa)
    cache[codigo] = datos
    return datos


def agregar_edades(df: pd.DataFrame, max_workers=5) -> pd.DataFrame:
    logger.info("Consultando edades de %s estudiantes...", len(df))

    codigos = df[["Codigo_estudiante", "Codigo_programa"]].dropna(subset="Codigo_estudiante").to_dict("records")
    total = len(codigos)
    cache = {}
    resultados = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futuros = {
            executor.submit(
                _fetch_estudiante,
                str(r["Codigo_estudiante"]).strip(),
                str(r.get("Codigo_programa", "")).strip() or None,
                cache,
            ): r for r in codigos
        }
        for i, futuro in enumerate(as_completed(futuros), 1):
            datos = futuro.result()
            resultados.append(datos)
            if i % 50 == 0 or i == total:
                logger.info("[%s/%s] estudiantes procesados", i, total)

    map_cache = {}
    for r in codigos:
        c = str(r["Codigo_estudiante"]).strip()
        map_cache[c] = cache.get(c, {})

    df = df.copy()
    df["Fecha_nacimiento"] = df["Codigo_estudiante"].apply(
        lambda c: map_cache.get(str(c).strip(), {}).get("Fecha_nacimiento")
    )
    df["Edad"] = df["Fecha_nacimiento"].apply(calcular_edad)
    df["Genero"] = df["Codigo_estudiante"].apply(
        lambda c: map_cache.get(str(c).strip(), {}).get("Genero")
    )

    return df