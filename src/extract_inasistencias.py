import logging
from datetime import datetime

import pandas as pd
import requests
import time

from .config import BASE_URL, HEADERS, FECHA_INICIO_INASISTENCIAS
from .utils import request_with_retry, guardar_csv, guardar_parquet

logger = logging.getLogger(__name__)


def obtener_inasistencias(fecha_inicio, fecha_fin, limit=5000):

    offset = 0
    todos = []

    while True:
        params = {
            "Fecha_inicio_inasistencia": fecha_inicio,
            "Fecha_fin_inasistencia": fecha_fin,
            "Limit": limit,
            "Offset": offset
        }

        response = request_with_retry(
            requests.get,
            f"{BASE_URL}/inasistencias",
            headers=HEADERS,
            params=params
        )

        logger.info("Inasistencias | Offset %s | Status %s", offset, response.status_code)

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


def ejecutar_extraccion_inasistencias():

    fecha_fin = datetime.now().strftime("%Y-%m-%d")

    logger.info("=== EXTRAYENDO INASISTENCIAS [%s → %s] ===", FECHA_INICIO_INASISTENCIAS, fecha_fin)

    raw = obtener_inasistencias(FECHA_INICIO_INASISTENCIAS, fecha_fin)

    detalle = []
    agregado = []

    for estudiante in raw:
        id_est = estudiante.get("Numero_identificacion_estudiante", "")
        nombre_completo = " ".join(filter(None, [
            estudiante.get("Primer_nombre", ""),
            estudiante.get("Segundo_nombre", ""),
            estudiante.get("Primer_apellido", ""),
            estudiante.get("Segundo_apellido", ""),
        ])).strip()

        for curso in estudiante.get("Cursos", []):
            curso_info = {
                "Numero_identificacion_estudiante": id_est,
                "Nombre_completo_estudiante": nombre_completo,
                "Sexo": estudiante.get("Sexo"),
                "Correo_electronico": estudiante.get("Correo_electronico_personal"),
                "Celular": estudiante.get("Celular"),
                "Codigo_curso": curso.get("Codigo_curso"),
                "Nombre_curso": curso.get("Nombre_curso"),
                "Codigo_modulo": curso.get("Codigo_modulo"),
                "Nombre_modulo": curso.get("Nombre_modulo"),
                "Horario_curso": curso.get("Horario_curso"),
                "Periodo_curso": curso.get("Periodo_curso"),
                "Numero_identificacion_docente": curso.get("Numero_identificacion_docente"),
                "Nombre_docente": curso.get("Nombre_docente"),
                "Cantidad_inasistencia": curso.get("Cantidad_inasistencia"),
            }

            agregado.append(curso_info)

            for falta in curso.get("Inasistencias", []):
                detalle.append({
                    **curso_info,
                    "Dia": falta.get("Dia"),
                    "Fecha_inasistencia": falta.get("Fecha"),
                    "Hora": falta.get("Hora"),
                    "Justificacion": falta.get("Justificacion"),
                    "Detalle_justificacion": falta.get("Detalle_justificacion"),
                })

    df_agregado = pd.DataFrame(agregado)
    df_detalle = pd.DataFrame(detalle)

    for df_tmp in [df_agregado, df_detalle]:
        df_tmp["Nombre_modulo"] = df_tmp["Nombre_modulo"].str.replace(
            r"^\d+-\s*", "", regex=True
        )

    modulos_excluir = [
        "CIES-Univ-001", "CIES-Univ-002", "CIES-Univ-003",
        "CIES-Univ-005", "CIES-Univ-006", "CIES-Univ-004",
        "TecLab-AuxAdmin-004", "TecLab-MarkDig-004", "TecLab-001",
    ]
    antes_ag = len(df_agregado)
    antes_det = len(df_detalle)
    df_agregado = df_agregado[~df_agregado["Codigo_modulo"].isin(modulos_excluir)].copy()
    df_detalle = df_detalle[~df_detalle["Codigo_modulo"].isin(modulos_excluir)].copy()
    logger.info(
        "Módulos excluidos: agregado %s→%s, detalle %s→%s",
        antes_ag, len(df_agregado), antes_det, len(df_detalle),
    )

    guardar_parquet(df_agregado, "inasistencias_agregado.parquet")
    guardar_csv(df_agregado, "inasistencias_agregado.csv")

    guardar_parquet(df_detalle, "inasistencias_detalle.parquet")
    guardar_csv(df_detalle, "inasistencias_detalle.csv")

    logger.info("Inasistencias agregado: %s registros", len(df_agregado))
    logger.info("Inasistencias detalle: %s registros", len(df_detalle))

    return df_agregado, df_detalle
