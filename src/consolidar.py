import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def _separar_sede_programa(nombre):
    if pd.isna(nombre):
        return "", ""
    partes = str(nombre).split(" - ")
    sede = partes[0].strip()
    programa = partes[-1].strip() if len(partes) > 1 else ""
    return sede, programa


CLASIFICACION_COLS = [
    "Codigo_sede", "Nombre_sede",
    "Codigo_jornada", "Nombre_jornada",
    "Codigo_programa",
    "Consecutivo_grupo", "Nombre_grupo",
    "Codigo_nivel", "Nombre_nivel",
    "Condicion_matricula",
    "Genero",
]


def _cargar_clasificacion_estudiantes() -> pd.DataFrame:

    df = pd.read_parquet("data/raw/estudiantes.parquet")

    cols = [c for c in CLASIFICACION_COLS if c in df.columns]
    df_clasif = df[["Numero_identificacion"] + cols].copy()

    df_clasif = df_clasif.sort_values("Numero_identificacion")
    df_clasif = df_clasif.drop_duplicates(subset="Numero_identificacion", keep="last")

    return df_clasif


def consolidar_notas_cursos(df_notas_pivot=None, df_cursos=None, df_estudiantes=None):

    logger.info("=== CONSOLIDANDO NOTAS + CURSOS + ESTUDIANTES ===")

    if df_notas_pivot is None:
        df_notas_pivot = pd.read_parquet("data/raw/notas_pivot.parquet")

    if df_cursos is None:
        df_cursos = pd.read_parquet("data/raw/cursos.parquet")

    if df_estudiantes is None:
        if Path("data/raw/estudiantes.parquet").exists():
            df_estudiantes = _cargar_clasificacion_estudiantes()
        else:
            df_estudiantes = None

    notas = df_notas_pivot.copy()

    notas["Sede"], notas["Nombre_programa_limpio"] = zip(
        *notas["Nombre_programa"].apply(_separar_sede_programa)
    )

    if df_estudiantes is not None:
        id_col = "Numero_identificacion_estudiante" if "Numero_identificacion_estudiante" in notas.columns else "Numero_identificacion"
        df_est = df_estudiantes.rename(columns={"Numero_identificacion": id_col})
        antes = len(notas)
        notas = notas.merge(df_est, on=id_col, how="left")
        despues = len(notas)
        clasif_count = notas[CLASIFICACION_COLS[0]].notna().sum()
        logger.info(
            "Clasificación merge: %s → %s filas, %s con clasificación",
            antes, despues, clasif_count
        )

    Path("data/processed").mkdir(parents=True, exist_ok=True)

    path = "data/processed/consolidado_notas"
    try:
        notas.to_csv(f"{path}.csv", index=False, encoding="utf-8-sig")
    except PermissionError:
        logger.warning("No se pudo guardar %s.csv (archivo abierto en otro programa)", path)
    notas.to_parquet(f"{path}.parquet", index=False)

    logger.info("Consolidado notas guardado: %s filas × %s columnas", *notas.shape)

    return notas


def generar_resumen_informe(df_consolidado=None):

    logger.info("=== GENERANDO RESUMEN DEL INFORME ===")

    if df_consolidado is None:
        df_consolidado = pd.read_parquet("data/processed/consolidado_notas.parquet")

    resumenes = {}

    resumenes["promedio_por_programa"] = (
        df_consolidado.groupby("Nombre_programa_limpio")["Promedio_evaluacion"]
        .agg(["count", "mean", "median", "std", "min", "max"])
        .round(2)
    )

    resumenes["promedio_por_sede"] = (
        df_consolidado.groupby("Sede")["Promedio_evaluacion"]
        .agg(["count", "mean", "median"])
        .round(2)
    )

    resumenes["inasistencias_por_programa"] = (
        df_consolidado.groupby("Nombre_programa_limpio")
        .agg(
            total_estudiantes=("Promedio_evaluacion", "count"),
            promedio_inasistencia=("Porcentaje_inasistencia", "mean"),
        )
        .round(2)
    )

    if "Nombre_jornada" in df_consolidado.columns:
        resumenes["promedio_por_jornada"] = (
            df_consolidado.groupby("Nombre_jornada")["Promedio_evaluacion"]
            .agg(["count", "mean", "median"])
            .round(2)
        )

    if "Codigo_nivel" in df_consolidado.columns:
        resumenes["promedio_por_nivel"] = (
            df_consolidado.groupby("Codigo_nivel")["Promedio_evaluacion"]
            .agg(["count", "mean", "median"])
            .round(2)
        )

    Path("data/processed").mkdir(parents=True, exist_ok=True)
    path = "data/processed/resumen_informe.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for nombre, df in resumenes.items():
            df.to_excel(writer, sheet_name=nombre[:31])

    logger.info("Resumen guardado en: %s", path)

    return resumenes
