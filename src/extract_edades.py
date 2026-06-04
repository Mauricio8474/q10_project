import logging

import requests
import pandas as pd
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
        if response.status_code != 200:
            logger.warning("Status %s para estudiante %s", response.status_code, codigo_estudiante)
            return {}
        return response.json()
    except Exception as e:
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

def agregar_edades(df: pd.DataFrame) -> pd.DataFrame:
    fechas, edades, generos = [], [], []
    total = len(df)

    # Caché para no consultar el mismo estudiante dos veces
    cache = {}

    for i, row in df.iterrows():
        codigo_estudiante = str(row.get("Codigo_estudiante", "")).strip()
        codigo_programa   = str(row.get("Codigo_programa", "")).strip() or None

        if not codigo_estudiante:
            fechas.append(None)
            edades.append(None)
            generos.append(None)
            continue

        if codigo_estudiante not in cache:
            datos = obtener_datos_estudiante(codigo_estudiante, codigo_programa)
            cache[codigo_estudiante] = datos
            time.sleep(0.15)
        else:
            datos = cache[codigo_estudiante]

        fecha  = datos.get("Fecha_nacimiento") or None
        genero = datos.get("Genero") or None
        edad   = calcular_edad(fecha)

        fechas.append(fecha)
        edades.append(edad)
        generos.append(genero)

        if (i + 1) % 50 == 0 or (i + 1) == total:
            logger.info("[%s/%s] %s → Edad: %s | Género: %s", i + 1, total, codigo_estudiante, edad, genero)

    df = df.copy()
    df["Fecha_nacimiento"] = fechas
    df["Edad"]             = edades
    df["Genero"]           = generos

    return df