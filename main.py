import argparse
import logging
import os
import sys

import pandas as pd

from src.utils import setup_logging, resumen_dataframe, guardar_csv, guardar_parquet

setup_logging()
logger = logging.getLogger(__name__)


def cmd_estudiantes():
    from src.extract_estudiantes import ejecutar_extraccion_estudiantes

    df = ejecutar_extraccion_estudiantes()
    resumen_dataframe(df)


def cmd_cancelados():
    from src.extract_cancelados import ejecutar_extraccion
    from src.extract_edades import agregar_edades

    logger.info("=== EXTRAYENDO CANCELADOS ===")
    df = ejecutar_extraccion()
    logger.info("Total registros extraídos: %s", len(df))

    logger.info("=== CONSULTANDO FECHAS DE NACIMIENTO ===")
    df = agregar_edades(df)

    logger.info("Registros con edad calculada: %s", df["Edad"].notna().sum())
    logger.info("Registros sin fecha de nacimiento: %s", df["Edad"].isna().sum())

    resumen_dataframe(df)
    os.makedirs("data/raw", exist_ok=True)
    guardar_csv(df, "cancelados.csv")
    df.to_parquet("data/raw/cancelados.parquet", index=False)

    ruta_excel = "data/raw/cancelados.xlsx"
    df.to_excel(ruta_excel, index=False, sheet_name="Cancelados")
    logger.info("Excel generado: %s", ruta_excel)


def cmd_cursos():
    from src.extract_cursos import ejecutar_extraccion_cursos

    df = ejecutar_extraccion_cursos()
    resumen_dataframe(df)


def cmd_notas():
    from src.extract_notas import ejecutar_extraccion_notas
    from src.transform_notas import transformar_notas

    df_raw = ejecutar_extraccion_notas()
    df_pivot = transformar_notas(df_raw)

    ruta_cancelados = "data/raw/cancelados.parquet"
    if os.path.exists(ruta_cancelados):
        cancelados = pd.read_parquet(ruta_cancelados)
        ids_cancelados = cancelados["Numero_identificacion"].unique()
        antes = len(df_pivot)
        df_pivot = df_pivot[~df_pivot["Numero_identificacion_estudiante"].isin(ids_cancelados)].copy()
        logger.info("Estudiantes cancelados eliminados de notas: %s registros", antes - len(df_pivot))
        guardar_parquet(df_pivot, "notas_pivot.parquet")
        guardar_csv(df_pivot, "notas_pivot.csv")

    resumen_dataframe(df_pivot)


def cmd_inasistencias():
    from src.extract_inasistencias import ejecutar_extraccion_inasistencias
    from src.analisis_inasistencias import enriquecer_inasistencias

    df_agregado, df_detalle = ejecutar_extraccion_inasistencias()
    logger.info("Agregado: %s registros", len(df_agregado))
    logger.info("Detalle: %s registros", len(df_detalle))

    try:
        df_est = pd.read_parquet("data/raw/estudiantes.parquet")
    except FileNotFoundError:
        logger.warning("estudiantes.parquet no encontrado — saltando enriquecimiento de inasistencias")
        return

    df_enriquecido = enriquecer_inasistencias(df_detalle, df_est)
    guardar_parquet(df_enriquecido, "inasistencias_enriquecido.parquet")
    guardar_csv(df_enriquecido, "inasistencias_enriquecido.csv")


def cmd_consolidar():
    from src.consolidar import consolidar_notas_cursos, generar_resumen_informe

    df_consol = consolidar_notas_cursos()
    generar_resumen_informe(df_consol)


def cmd_excel():
    from src.generar_excel import generar_excel_revision

    generar_excel_revision()


def cmd_reporte():
    from src.reporte_bajo_rendimiento import generar_reporte_bajo_rendimiento

    generar_reporte_bajo_rendimiento()


def cmd_todo():
    cmd_cursos()
    cmd_cancelados()
    cmd_notas()
    cmd_inasistencias()
    cmd_estudiantes()
    cmd_consolidar()
    cmd_excel()
    cmd_reporte()


def main():
    parser = argparse.ArgumentParser(description="q10_project — ETL académico USM")
    parser.add_argument(
        "comando",
        nargs="?",
        default="todo",
        choices=["cancelados", "cursos", "notas", "inasistencias", "estudiantes", "consolidar", "excel", "reporte", "todo"],
        help="Módulo a ejecutar (default: todo)"
    )

    args = parser.parse_args()

    {
        "cancelados": cmd_cancelados,
        "cursos": cmd_cursos,
        "notas": cmd_notas,
        "inasistencias": cmd_inasistencias,
        "estudiantes": cmd_estudiantes,
        "consolidar": cmd_consolidar,
        "excel": cmd_excel,
        "reporte": cmd_reporte,
        "todo": cmd_todo,
    }[args.comando]()


if __name__ == "__main__":
    main()
