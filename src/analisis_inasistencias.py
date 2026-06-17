import logging

import pandas as pd

from .config import (
    CALENDARIO_2_SEMESTRE,
    CORTES_A,
    CORTES_B,
    ETIQUETAS_A,
    ETIQUETAS_B,
)

logger = logging.getLogger(__name__)


def _es_sede_valida(sede, sedes_permitidas):
    return pd.notna(sede) and sede.strip().upper() in [s.upper() for s in sedes_permitidas]


_SEDES_MODA = ["INEM"]
_SEDES_TURISMO_MARKETING = ["MINCA", "BURITACA"]
_PROGRAMA_MODA = "TECNOLOGÍA EN GESTIÓN DE PRODUCCIÓN DE MODAS"
_PROGRAMA_TURISMO = "TECNOLOGÍA EN GESTIÓN DEL TURISMO CULTURAL Y DE NATURALEZA"
_PROGRAMA_MARKETING = "TECNOLOGÍA EN MARKETING DIGITAL"


def _extraer_numero_semestre(nombre_nivel):
    if pd.isna(nombre_nivel):
        return None
    s = nombre_nivel.strip()
    for palabra in s.split():
        if palabra.isdigit():
            return palabra
    return None


def _asignar_grupo_estudiante(programa, sede, nombre_nivel=None):
    if pd.isna(programa):
        return "A"
    prog = programa.strip().upper()
    sem_num = _extraer_numero_semestre(nombre_nivel)
    es_semestre_1 = sem_num == CALENDARIO_2_SEMESTRE
    if not es_semestre_1:
        return "A"
    # Moda solo en INEM
    if prog == _PROGRAMA_MODA:
        return "B" if _es_sede_valida(sede, _SEDES_MODA) else "A"
    # Turismo solo en MINCA / BURITACA
    if prog == _PROGRAMA_TURISMO:
        return "B" if _es_sede_valida(sede, _SEDES_TURISMO_MARKETING) else "A"
    # Marketing solo en MINCA / BURITACA
    if prog == _PROGRAMA_MARKETING:
        return "B" if _es_sede_valida(sede, _SEDES_TURISMO_MARKETING) else "A"
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

    antes = len(df)
    df = df[df["Nombre_programa_limpio"].notna() & (df["Nombre_programa_limpio"].str.strip() != "")].copy()
    eliminados = antes - len(df)
    if eliminados:
        logger.info("Registros sin programa (excluidos): %s", eliminados)

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
