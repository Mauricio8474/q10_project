import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def _agrupar_inasistencias(df, groupby_cols):
    return df.groupby(groupby_cols).agg(
        Total_estudiantes=("Numero_identificacion_estudiante", "nunique"),
        Total_inasistencias=("Cantidad_inasistencia", "sum"),
        Promedio_inasistencias=("Cantidad_inasistencia", "mean"),
    ).reset_index().round({"Promedio_inasistencias": 1}).sort_values(
        "Promedio_inasistencias", ascending=False
    ).reset_index(drop=True)


def _cruzada(df, index_col):
    return df.groupby([index_col, "Seguimiento"]).size().unstack(
        fill_value=0
    ).reset_index().fillna(0)


def generar_reporte_inasistencias():
    logger.info("=== GENERANDO REPORTE DE INASISTENCIAS ===")

    ruta = Path("data/raw/inasistencias_enriquecido.csv")
    if not ruta.exists():
        logger.error("Archivo faltante: %s — ejecute 'python main.py rapido' primero", ruta)
        return {}

    try:
        df = pd.read_csv(ruta, low_memory=False)
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        logger.error("Error al leer %s: %s", ruta, e)
        return {}

    logger.info("Registros cargados: %s", len(df))

    tablas = {
        "inasistencias_programa": _agrupar_inasistencias(df, ["Nombre_programa_limpio", "Sede", "Nombre_nivel"]),
        "inasistencias_modulo": _agrupar_inasistencias(df, ["Nombre_modulo", "Nombre_programa_limpio"]),
        "inasistencias_seguimiento": _agrupar_inasistencias(df, ["Seguimiento", "Grupo", "Nombre_programa_limpio"]),
        "inasistencias_sede": _agrupar_inasistencias(df, ["Sede"]),
        "cruzada_programa_seguimiento": _cruzada(df, "Nombre_programa_limpio"),
        "cruzada_sede_seguimiento": _cruzada(df, "Sede"),
        "resumen_estudiantes": df.groupby(
            ["Nombre_completo_estudiante", "Numero_identificacion_estudiante"]
        ).agg(
            Total_inasistencias=("Cantidad_inasistencia", "sum"),
            Modulos_distintos=("Nombre_modulo", "nunique"),
            Sede=("Sede", "first"),
            Programa=("Nombre_programa_limpio", "first"),
        ).reset_index().sort_values("Total_inasistencias", ascending=False).reset_index(drop=True),
        "inasistencias_asignatura": df.groupby([
            "Nombre_completo_estudiante", "Nombre_programa_limpio", "Sede",
            "Nombre_modulo", "Seguimiento",
        ]).agg(
            Inasistencias_Totales=("Seguimiento", "count"),
        ).reset_index().sort_values("Inasistencias_Totales", ascending=False).reset_index(drop=True),
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
