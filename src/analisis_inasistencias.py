import logging

import pandas as pd

from .config import (
    PROGRAMAS_GRUPO_B,
    SEDES_GRUPO_B,
    CORTES_A,
    CORTES_B,
    ETIQUETAS_A,
    ETIQUETAS_B,
)

logger = logging.getLogger(__name__)


def _asignar_grupo_estudiante(programa, sede):
    if (
        (programa and programa.strip().upper() in [p.upper() for p in PROGRAMAS_GRUPO_B])
        or (sede and sede.strip().upper() in [s.upper() for s in SEDES_GRUPO_B])
    ):
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

    est = df_estudiantes[["Numero_identificacion", "Nombre_programa_limpio", "Sede"]].drop_duplicates(
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
            r.get("Nombre_programa_limpio"), r.get("Sede")
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
