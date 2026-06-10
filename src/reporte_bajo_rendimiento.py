import logging
import os
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


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

    df["bajo"] = (df["Nota final"] < 3.0) & (df["Nota final"] > 1)
    df["condicion_de_alerta"] = (df["Nota final"] <= 1) & (df["Nota final"] >= 0)
    df["Area"] = df["Nombre_asignatura"].apply(_asignar_area)

    tablas = {
        "bajo_rendimiento_area": _tabla_area(df),
        "bajo_rendimiento_asignatura": _tabla_asignatura(df),
        "bajo_rendimiento_curso": _tabla_curso(df),
        "estudiantes_revision": _tabla_estudiantes_revision(df),
    }

    Path("data/reportes").mkdir(parents=True, exist_ok=True)

    for nombre, tabla in tablas.items():
        ruta = f"data/reportes/{nombre}.csv"
        tabla.to_csv(ruta, index=False, encoding="utf-8-sig")
        logger.info("CSV guardado: %s (%s filas)", ruta, len(tabla))

    ruta_excel = "data/reportes/bajo_rendimiento.xlsx"
    with pd.ExcelWriter(ruta_excel, engine="openpyxl") as writer:
        for nombre, tabla in tablas.items():
            nombre_hoja = nombre.replace("bajo_rendimiento_", "")[:31]
            tabla.to_excel(writer, sheet_name=nombre_hoja, index=False)
    logger.info("Excel generado: %s", ruta_excel)

    return tablas


def _asignar_area(nombre):
    import unicodedata
    nombre = str(nombre).strip()
    nombre = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode("ascii").upper()
    m = {
        "Logistica y Comercio": [
            "GESTION NAVIERA Y PORTUARIA",
            "INTRODUCCION AL COMERCIO EXTERIOR",
            "INTRODUCCION A LA LOGISTICA",
            "INFRAESTRUCTURA PORTUARIA",
            "LOGISTICA COMERCIAL",
            "LEGISLACION COMERCIAL Y ADUANERA",
        ],
        "Marketing y Ventas": [
            "INTRODUCCION AL MARKETING DIGITAL",
            "GESTION DE PRECIOS Y PERCEPCION DE VALOR",
            "SEO Y SEM POSICIONAMIENTO WEB",
            "ESTRATEGIAS DE CONTENIDO EN REDES SOCIALES",
        ],
        "Turismo": [
            "ORGANIZACION DE SERVICIOS EN AGENCIAS DE VIAJES",
            "ETNOTURISMO Y DESARROLLO COMUNITARIO",
            "SOSTENIBILIDAD Y TURISMO REGENERATIVO",
            "LEGISLACION EN LA INDUSTRIA TURISTICA",
            "ETIQUETA Y PROTOCOLO EN SERVICIOS TURISTICOS",
            "FUNDAMENTOS DE LA OPERACION TURISTICA",
        ],
        "Idiomas": [
            "INGLES I",
            "INGLES II",
        ],
        "Matematicas y Estadistica": [
            "RAZONAMIENTO CUANTITATIVO",
            "PROBABILIDAD Y ESTADISTICA",
            "ESTADISTICA",
            "ALGEBRA Y GEOMETRIA ANALITICA",
            "CALCULO DIFERENCIAL",
        ],
        "Comunicacion": [
            "COMUNICACION ESCRITA",
            "EXPRESION ORAL Y ARGUMENTACION",
            "LECTOESCRITURA Y COMUNICACION TECNICA",
        ],
        "Formacion Integral": [
            "ETICA PROFESIONAL EN LOS NEGOCIOS",
            "COMPETENCIAS HUMANAS Y DESARROLLO INTEGRAL",
            "CATEDRA USM Y CONTEXTO SAMARIO",
            "TALLER DE CREATIVIDAD E INNOVACION",
        ],
        "Tecnologia y Datos": [
            "HERRAMIENTAS TICS",
            "HERRAMIENTAS TECNOLOGICAS APLICADAS I",
            "MINERIA DE DATOS I",
        ],
        "Diseno y Modas": [
            "PATRONAJE Y ESCALADO",
            "TECNICAS DE CONFECCION I",
            "PRODUCCION DE MODAS",
            "HISTORIA DE LA MODA E INDUMENTARIA",
        ],
        "Gastronomia": [
            "CULTURA Y GASTRONOMIA",
            "MIXOLOGIA Y COCTELERIA",
            "GASTRONOMIA II",
            "SST Y BPM",
            "GASTRONOMIA I",
            "BIOQUIMICA",
        ],
        "Administracion y Costos": [
            "ADMINISTRACION DE ORGANIZACIONES",
            "COSTOS Y PRESUPUESTOS",
        ],
    }
    for area, materias in m.items():
        if nombre in materias:
            return area
    return "Otra"


def _tabla_area(df):
    return df.groupby("Area").agg(
        Total_estudiantes=("bajo", "count"),
        Bajo_rendimiento=("bajo", "sum"),
        Porcentaje_bajo=("bajo", "mean")
    ).reset_index().assign(
        Porcentaje_bajo=lambda x: (x["Porcentaje_bajo"] * 100).round(1)
    ).sort_values("Porcentaje_bajo", ascending=False).reset_index(drop=True)


def _tabla_asignatura(df):
    return df.groupby(["Codigo_asignatura", "Nombre_asignatura", "Area"]).agg(
        Total_estudiantes=("bajo", "count"),
        Bajo_rendimiento=("bajo", "sum"),
        Porcentaje_bajo=("bajo", "mean")
    ).reset_index().assign(
        Porcentaje_bajo=lambda x: (x["Porcentaje_bajo"] * 100).round(1)
    ).sort_values("Porcentaje_bajo", ascending=False).reset_index(drop=True)


def _tabla_curso(df):
    return df.groupby(["Nombre_curso", "Sede", "Nombre_programa_limpio", "Area"]).agg(
        Total_estudiantes=("bajo", "count"),
        Bajo_rendimiento=("bajo", "sum"),
        Porcentaje_bajo=("bajo", "mean")
    ).reset_index().assign(
        Porcentaje_bajo=lambda x: (x["Porcentaje_bajo"] * 100).round(1)
    ).sort_values("Porcentaje_bajo", ascending=False).reset_index(drop=True)


def _tabla_estudiantes_revision(df):
    return df[df["condicion_de_alerta"]][
        ["Nombre_completo_estudiante", "Numero_identificacion_estudiante", "Sede", "Nombre_programa_limpio", "Nombre_asignatura", "Nota final"]
    ].drop_duplicates().reset_index(drop=True)
