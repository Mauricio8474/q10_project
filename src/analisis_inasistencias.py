import logging

import pandas as pd

from .config import (
    PROGRAMAS_GRUPO_B,
    SEDES_GRUPO_B_MODA,
    SEMESTRE_GRUPO_B,
    CORTES_A,
    CORTES_B,
    ETIQUETAS_A,
    ETIQUETAS_B,
)

logger = logging.getLogger(__name__)


def _asignar_grupo_estudiante(programa, sede, nombre_nivel=None):
    if pd.isna(programa):
        return "A"
    prog = programa.strip().upper()
    # Semestre 1 check
    es_semestre_1 = (
        pd.notna(nombre_nivel)
        and nombre_nivel.strip().upper() == SEMESTRE_GRUPO_B.upper()
    )
    if not es_semestre_1:
        return "A"
    # Moda en INEM
    if any(p.upper() == prog for p in PROGRAMAS_GRUPO_B["MODA"]):
        if pd.notna(sede) and sede.strip().upper() in [s.upper() for s in SEDES_GRUPO_B_MODA]:
            return "B"
        return "A"
    # Logística
    if any(p.upper() == prog for p in PROGRAMAS_GRUPO_B["LOGISTICA"]):
        return "B"
    # Marketing
    if any(p.upper() == prog for p in PROGRAMAS_GRUPO_B["MARKETING"]):
        return "B"
    return "A"


def _clasificar_seguimiento(fecha, grupo):
    cortes = CORTES_B if grupo == "B" else CORTES_A
    etiquetas = ETIQUETAS_B if grupo == "B" else ETIQUETAS_A

    for i in range(len(etiquetas)):
        if cortes[i] <= fecha < cortes[i + 1]:
            return etiquetas[i]
    return None


def enriquecer_inasistencias(df_detalle, df_estudiantes):

    logger.info("=== ENRIQUECIENDO INASISTENCIAS (grupo + seguimiento) ===")

    df = df_detalle.copy()

    df["Fecha_inasistencia"] = pd.to_datetime(df["Fecha_inasistencia"], errors="coerce")

    est = df_estudiantes[["Numero_identificacion", "Nombre_programa_limpio", "Sede", "Nombre_nivel"]].drop_duplicates(
        subset="Numero_identificacion"
    )

    df = df.merge(
        est,
        left_on="Numero_identificacion_estudiante",
        right_on="Numero_identificacion",
        how="left",
    )

    df["Grupo"] = df.apply(
        lambda r: _asignar_grupo_estudiante(
            r.get("Nombre_programa_limpio"), r.get("Sede"), r.get("Nombre_nivel")
        ),
        axis=1,
    )

    df["Seguimiento"] = df.apply(
        lambda r: _clasificar_seguimiento(r["Fecha_inasistencia"], r["Grupo"])
        if pd.notna(r["Fecha_inasistencia"])
        else None,
        axis=1,
    )

    logger.info(
        "Inasistencias enriquecidas: %s registros, %s sin seguimiento",
        len(df),
        df["Seguimiento"].isna().sum(),
    )

    return df
