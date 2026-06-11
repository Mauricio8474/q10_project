import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("Q10_API_KEY")

BASE_URL = "https://api.q10.com/v1"

HEADERS = {
    "api-key": API_KEY
}

# ---------------------------------------------------
# Configuración del semestre (cambia cada periodo)
# ---------------------------------------------------

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "semestre.json"

with open(_CONFIG_PATH, encoding="utf-8") as _f:
    _SEMESTRE = json.load(_f)

PERIODOS = [_SEMESTRE["periodo"]]

PROGRAMAS = _SEMESTRE["programas"]

EXCLUIR_PROGRAMAS = _SEMESTRE["excluir_programas"]

FECHA_INICIO_INASISTENCIAS = _SEMESTRE["fecha_inicio_inasistencias"]
FECHA_FIN_INASISTENCIAS = None  # Se asigna en runtime con datetime.now()

# ---------------------------------------------------
# INASISTENCIAS — Grupos con fechas diferenciadas
# ---------------------------------------------------

_gb = _SEMESTRE["grupo_b"]
PROGRAMAS_GRUPO_B = {
    "MODA": _gb["moda"],
    "LOGISTICA": _gb["logistica"],
    "MARKETING": _gb["marketing"],
}
SEDES_GRUPO_B_MODA = _gb["sedes_moda"]
SEMESTRE_GRUPO_B = _gb["semestre"]

CORTES_A = pd.to_datetime(_SEMESTRE["cortes_a"])
CORTES_B = pd.to_datetime(_SEMESTRE["cortes_b"])

_etiq = _SEMESTRE["etiquetas_seguimiento"]
ETIQUETAS_A = _etiq
ETIQUETAS_B = _etiq
