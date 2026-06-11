import logging
import os
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def generar_reporte_inasistencias():
    logger.info("=== GENERANDO REPORTE DE INASISTENCIAS ===")

    ruta = "data/raw/inasistencias_enriquecido.csv"
    if not os.path.exists(ruta):
        logger.error("Archivo faltante: %s — ejecute 'python main.py rapido' primero", ruta)
        return {}

    df = pd.read_csv(ruta, low_memory=False)
    logger.info("Registros cargados: %s", len(df))

    tablas = {
        "inasistencias_programa": _tabla_programa(df),
        "inasistencias_modulo": _tabla_modulo(df),
        "inasistencias_seguimiento": _tabla_seguimiento(df),
        "inasistencias_sede": _tabla_sede(df),
        "cruzada_programa_seguimiento": _cruzada_programa_seguimiento(df),
        "cruzada_sede_seguimiento": _cruzada_sede_seguimiento(df),
        "resumen_estudiantes": _resumen_estudiantes(df),
        "inasistencias_asignatura": _tabla_asignatura_estudiante(df),
    }

    Path("data/reportes").mkdir(parents=True, exist_ok=True)

    for nombre, tabla in tablas.items():
        ruta_csv = f"data/reportes/{nombre}.csv"
        tabla.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
        logger.info("CSV guardado: %s (%s filas)", ruta_csv, len(tabla))

    ruta_excel = "data/reportes/inasistencias.xlsx"
    with pd.ExcelWriter(ruta_excel, engine="openpyxl") as writer:
        for nombre, tabla in tablas.items():
            nombre_hoja = nombre.replace("inasistencias_", "").replace("cruzada_", "cruz_")[:31]
            tabla.to_excel(writer, sheet_name=nombre_hoja, index=False)
    logger.info("Excel generado: %s", ruta_excel)

    return tablas


def _tabla_programa(df):
    return df.groupby(["Nombre_programa_limpio", "Sede", "Nombre_nivel"]).agg(
        Total_estudiantes=("Numero_identificacion_estudiante", "nunique"),
        Total_inasistencias=("Cantidad_inasistencia", "sum"),
        Promedio_inasistencias=("Cantidad_inasistencia", "mean"),
    ).reset_index().round({"Promedio_inasistencias": 1}).sort_values(
        "Promedio_inasistencias", ascending=False
    ).reset_index(drop=True)


def _tabla_modulo(df):
    return df.groupby(["Nombre_modulo", "Nombre_programa_limpio"]).agg(
        Total_estudiantes=("Numero_identificacion_estudiante", "nunique"),
        Total_inasistencias=("Cantidad_inasistencia", "sum"),
        Promedio_inasistencias=("Cantidad_inasistencia", "mean"),
    ).reset_index().round({"Promedio_inasistencias": 1}).sort_values(
        "Promedio_inasistencias", ascending=False
    ).reset_index(drop=True)


def _tabla_seguimiento(df):
    return df.groupby(["Seguimiento", "Grupo", "Nombre_programa_limpio"]).agg(
        Total_estudiantes=("Numero_identificacion_estudiante", "nunique"),
        Total_inasistencias=("Cantidad_inasistencia", "sum"),
        Promedio_inasistencias=("Cantidad_inasistencia", "mean"),
    ).reset_index().round({"Promedio_inasistencias": 1}).sort_values(
        "Promedio_inasistencias", ascending=False
    ).reset_index(drop=True)


def _tabla_sede(df):
    return df.groupby("Sede").agg(
        Total_estudiantes=("Numero_identificacion_estudiante", "nunique"),
        Total_inasistencias=("Cantidad_inasistencia", "sum"),
        Promedio_inasistencias=("Cantidad_inasistencia", "mean"),
    ).reset_index().round({"Promedio_inasistencias": 1}).sort_values(
        "Promedio_inasistencias", ascending=False
    ).reset_index(drop=True)


def _cruzada_programa_seguimiento(df):
    return df.groupby(["Nombre_programa_limpio", "Seguimiento"]).size().unstack(
        fill_value=0
    ).reset_index().fillna(0)


def _cruzada_sede_seguimiento(df):
    return df.groupby(["Sede", "Seguimiento"]).size().unstack(
        fill_value=0
    ).reset_index().fillna(0)


def _resumen_estudiantes(df):
    return df.groupby(["Nombre_completo_estudiante", "Numero_identificacion_estudiante"]).agg(
        Total_inasistencias=("Cantidad_inasistencia", "sum"),
        Modulos_distintos=("Nombre_modulo", "nunique"),
        Sede=("Sede", "first"),
        Programa=("Nombre_programa_limpio", "first"),
    ).reset_index().sort_values(
        "Total_inasistencias", ascending=False
    ).reset_index(drop=True)


def _tabla_asignatura_estudiante(df):
    return df.groupby([
        "Nombre_completo_estudiante", "Nombre_programa_limpio", "Sede",
        "Nombre_modulo", "Seguimiento",
    ]).agg(
        Inasistencias_Totales=("Seguimiento", "count"),
    ).reset_index().sort_values(
        "Inasistencias_Totales", ascending=False
    ).reset_index(drop=True)
