import os

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("Q10_API_KEY")

BASE_URL = "https://api.q10.com/v1"

HEADERS = {
    "api-key": API_KEY
}

PERIODOS = [5, 6]

PROGRAMAS = [
    "Tecnolog-Logis-Bas",
    "Tecnolog-Gastro-Inem",
    "Tecnolog-Mkt-Bas",
    "Tecnolog-Turis-Bur",
    "Tecnolog-Logis-Inem",
    "Tecnolog-Mkt-Bur",
    "Pro-Arq-Inem",
    "Pro-Mod-Inem",
    "Tecnolog-Mod-Inem",
    "Pro-Agro-Inem",
    "Pro-Datos-Inem",
    "Pro-Agua-Inem",
    "Pro-Elec-Inem",
    "Pro-Topo-Inem",
    "Tecnolog-Datos-Inem",
    "Tecnolog-Arq-Inem",
    "Tecnolog-Agro-Inem",
    "Tecnolog-Elec-Inem",
    "Tecnolog-Agua-Inem",
    "Tecnolog-Turis-Inem",
    "Tecnolog-Topo-Inem",
    "Tecnolog-Mkt-Inem",
    "Tecnolog-Logis",
    "Tecnolog-Gastro",
    "Tecnolog-Turis",
    "Tecnolog-Mkt",
    "Tecnolog-Gastro-Ine",
    "Tecnolog-Turis-Ine",
    "Tecnolog-Turis-Min",
    "Tecnolog-Mkt-Min",
    "Tecnolog-Logis-Pes",
    "Tecnolog-Gastro-Pes",
    "Tecnolog-Mkt-Pes"
]

# ---------------------------------------------------
# INASISTENCIAS — Rango de fechas
# ---------------------------------------------------

FECHA_INICIO_INASISTENCIAS = "2026-02-01"
FECHA_FIN_INASISTENCIAS = None  # Se asigna en runtime con datetime.now()

# ---------------------------------------------------
# INASISTENCIAS — Grupos con fechas diferenciadas
# ---------------------------------------------------

PROGRAMAS_GRUPO_B = ["TECNOLOGÍA EN GESTIÓN DE PRODUCCIÓN DE MODAS"]
SEDES_GRUPO_B = ["MINCA", "BURITACA"]

CORTES_A = pd.to_datetime([
    "2026-02-01", "2026-04-02", "2026-05-14", "2026-06-26"
])
ETIQUETAS_A = [
    "Seguimiento 1 (01 Feb – 01 Abr)",
    "Seguimiento 2 (02 Abr – 13 May)",
    "Seguimiento 3 (14 May – 25 Jun)",
]

CORTES_B = pd.to_datetime([
    "2026-04-06", "2026-05-10", "2026-06-14", "2026-07-26"
])
ETIQUETAS_B = [
    "Seguimiento 1 (06 Abr – 09 May)",
    "Seguimiento 2 (10 May – 13 Jun)",
    "Seguimiento 3 (14 Jun – 25 Jul)",
]
