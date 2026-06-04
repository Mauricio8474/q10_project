import os

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
