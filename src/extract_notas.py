import logging

import pandas as pd
import requests
import time

from .config import BASE_URL, HEADERS, PERIODOS
from .utils import request_with_retry, guardar_parquet

logger = logging.getLogger(__name__)


def obtener_notas_curso(consecutivo_curso):

    params = {"Consecutivo_curso": consecutivo_curso}

    response = request_with_retry(
        requests.get,
        f"{BASE_URL}/evaluaciones/cuantitativo/notas",
        headers=HEADERS,
        params=params
    )

    if response is None:
        logger.warning("Curso %s | Sin respuesta — saltando", consecutivo_curso)
        return None

    if response.status_code != 200:
        logger.warning("Curso %s | Status %s — saltando", consecutivo_curso, response.status_code)
        return None

    return response.json()


def ejecutar_extraccion_notas(df_cursos=None):

    logger.info("=== EXTRAYENDO NOTAS ===")

    if df_cursos is None:
        try:
            df_cursos = pd.read_parquet("data/raw/cursos.parquet")
        except FileNotFoundError:
            logger.error("No se encuentra data/raw/cursos.parquet — ejecute 'python main.py cursos' primero")
            return pd.DataFrame()

    cursos_periodo = df_cursos[
        df_cursos["Consecutivo_periodo"].isin(PERIODOS) &
        (df_cursos["Estado"] == "Abierto")
    ]
    cursos_ids = cursos_periodo["Consecutivo"].unique().tolist() if not cursos_periodo.empty else []

    logger.info("Cursos a procesar (periodos %s): %s", PERIODOS, len(cursos_ids))

    if not cursos_ids:
        logger.warning("No hay cursos para los periodos %s — devolviendo vacío", PERIODOS)
        return pd.DataFrame()

    registros = []

    for i, curso_id in enumerate(cursos_ids):
        data = obtener_notas_curso(curso_id)

        if data is None:
            continue

        cursos_lista = data if isinstance(data, list) else [data]

        for curso_data in cursos_lista:
            curso_info = {
                "Consecutivo_curso": curso_data.get("Consecutivo_curso"),
                "Nombre_curso": curso_data.get("Nombre_curso"),
                "Codigo_asignatura": curso_data.get("Codigo_asignatura"),
                "Nombre_asignatura": curso_data.get("Nombre_asignatura"),
                "Codigo_programa": curso_data.get("Codigo_programa"),
                "Nombre_programa": curso_data.get("Nombre_programa"),
                "Consecutivo_periodo": curso_data.get("Consecutivo_periodo"),
                "Nombre_periodo": curso_data.get("Nombre_periodo"),
                "Consecutivo_sede_jornada": curso_data.get("Consecutivo_sede_jornada"),
                "Nombre_sede_jornada": curso_data.get("Nombre_sede_jornada"),
                "Nombre_completo_docente": curso_data.get("Nombre_completo_docente"),
                "Numero_identificacion_docente": curso_data.get("Numero_identificacion_docente"),
            }

            for est in curso_data.get("Estudiantes", []):
                fila = {**curso_info}
                fila["Codigo_matricula"] = est.get("Codigo_matricula")
                fila["Numero_identificacion_estudiante"] = est.get("Numero_identificacion_estudiante")
                fila["Abreviatura_tipo_identificacion_estudiante"] = est.get("Abreviatura_tipo_identificacion_estudiante")
                fila["Nombre_completo_estudiante"] = est.get("Nombre_completo_estudiante")
                fila["Promedio_evaluacion"] = est.get("Promedio_evaluacion")
                fila["Porcentaje_evaluado"] = est.get("Porcentaje_evaluado")
                fila["Cantidad_inasistencia"] = est.get("Cantidad_inasistencia")
                fila["Porcentaje_inasistencia"] = est.get("Porcentaje_inasistencia")
                fila["Estudiante_formalizado"] = est.get("Estudiante_formalizado")
                fila["Observaciones"] = est.get("Observaciones")
                fila["Parametros_evaluacion"] = est.get("Parametros_evaluacion")
                registros.append(fila)

        if (i + 1) % 50 == 0 or (i + 1) == len(cursos_ids):
            logger.info("  Notas: %s/%s cursos procesados", i + 1, len(cursos_ids))

        time.sleep(0.1)

    df = pd.DataFrame(registros)

    guardar_parquet(df, "notas_raw.parquet")
    df.to_csv("data/raw/notas_raw.csv", index=False, encoding="utf-8-sig")

    logger.info("Notas raw guardadas: %s registros", len(df))

    return df
