import json
import logging
import unicodedata
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_MAPPING_PATH = Path(__file__).resolve().parent.parent / "data" / "mappings" / "asignaturas_area.json"
with open(_MAPPING_PATH, encoding="utf-8") as _f:
    _AREAS = json.load(_f)


def _normalizar(nombre):
    nombre = str(nombre).strip()
    return unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode("ascii").upper()


def _asignar_area(nombre):
    nombre = _normalizar(nombre)
    for area, materias in _AREAS.items():
        if nombre in materias:
            return area
    return "Otra"


def _tabla_agrupada(df, groupby_cols):
    return df.groupby(groupby_cols).agg(
        Total_estudiantes=("bajo", "count"),
        Bajo_rendimiento=("bajo", "sum"),
        Porcentaje_bajo=("bajo", "mean")
    ).reset_index().assign(
        Porcentaje_bajo=lambda x: (x["Porcentaje_bajo"] * 100).round(1)
    ).sort_values("Porcentaje_bajo", ascending=False).reset_index(drop=True)


def _generar_tablas_por_seguimiento(df, col_nota, sufijo):
    df = df.copy()
    df["bajo"] = (df[col_nota] < 3.0) & (df[col_nota] > 1)
    df["condicion_de_alerta"] = (df[col_nota] <= 1) & (df[col_nota] >= 0)

    cols_est = ["Nombre_completo_estudiante", "Numero_identificacion_estudiante",
                "Sede", "Nombre_programa_limpio", "Nombre_asignatura", "Grupo",
                "Primer Seguimiento", "Segundo Seguimiento", "Tercer Seguimiento", col_nota]

    return {
        f"area_{sufijo}": _tabla_agrupada(df, ["Area"]),
        f"asignatura_{sufijo}": _tabla_agrupada(df, ["Codigo_asignatura", "Nombre_asignatura", "Area"]),
        f"curso_{sufijo}": _tabla_agrupada(df, ["Nombre_curso", "Sede", "Nombre_programa_limpio", "Area"]),
        f"estudiantes_revision_{sufijo}": df[df["condicion_de_alerta"]][cols_est].drop_duplicates().reset_index(drop=True),
    }


def generar_reporte_bajo_rendimiento():
    logger.info("=== GENERANDO REPORTE DE BAJO RENDIMIENTO ===")

    try:
        notas = pd.read_csv("data/raw/notas_pivot.csv")
        est = pd.read_csv("data/raw/estudiantes.csv")
    except FileNotFoundError as e:
        logger.error("Archivo faltante: %s — ejecute 'python main.py todo' primero", e)
        return {}

    df = notas.merge(
        est[["Numero_identificacion", "Nombre_nivel", "Sede", "Nombre_programa_limpio"]],
        left_on="Numero_identificacion_estudiante",
        right_on="Numero_identificacion",
        how="left"
    )

    df["Area"] = df["Nombre_asignatura"].apply(_asignar_area)

    seguimientos = [
        ("Primer Seguimiento", "seg1"),
        ("Segundo Seguimiento", "seg2"),
        ("Tercer Seguimiento", "seg3"),
        ("Nota final", "final"),
    ]

    tablas = {}
    for col_nota, sufijo in seguimientos:
        tablas.update(_generar_tablas_por_seguimiento(df, col_nota, sufijo))

    Path("data/reportes").mkdir(parents=True, exist_ok=True)

    for nombre, tabla in tablas.items():
        ruta = f"data/reportes/bajo_rendimiento_{nombre}.csv"
        tabla.to_csv(ruta, index=False, encoding="utf-8-sig")
        logger.info("CSV guardado: %s (%s filas)", ruta, len(tabla))

    ruta_excel = "data/reportes/bajo_rendimiento.xlsx"
    with pd.ExcelWriter(ruta_excel, engine="openpyxl") as writer:
        for nombre, tabla in tablas.items():
            nombre_hoja = nombre[:31]
            tabla.to_excel(writer, sheet_name=nombre_hoja, index=False)
    logger.info("Excel generado: %s", ruta_excel)

    return tablas
