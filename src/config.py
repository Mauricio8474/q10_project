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

# ---------------------------------------------------
# INASISTENCIAS — Calendario 2 con fechas diferenciadas
# ---------------------------------------------------

_c2 = _SEMESTRE["calendario_2"]
CALENDARIO_2_PROGRAMAS_MODA = _c2["programas_moda"]
CALENDARIO_2_PROGRAMAS_TURISMO_MARKETING = _c2["programas_turismo_marketing"]
CALENDARIO_2_SEMESTRE = _c2["semestre"]

CORTES_A = pd.to_datetime(_SEMESTRE["cortes_a"])
CORTES_B = pd.to_datetime(_SEMESTRE["cortes_b"])

ETIQUETAS_A = _SEMESTRE["etiquetas_seguimiento"]
ETIQUETAS_B = ETIQUETAS_A[:]
