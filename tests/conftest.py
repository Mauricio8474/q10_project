import pandas as pd
import pytest


@pytest.fixture
def df_inasistencias_muestra():
    return pd.DataFrame({
        "Numero_identificacion_estudiante": ["1", "2", "1", "3", "2"],
        "Nombre_completo_estudiante": ["Ana", "Luis", "Ana", "Eva", "Luis"],
        "Nombre_programa_limpio": [
            "TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS",
            "TECNOLOGÍA EN MARKETING DIGITAL",
            "TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS",
            "TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS",
            "TECNOLOGÍA EN MARKETING DIGITAL",
        ],
        "Sede": ["BASTIDAS", "MINCA", "BASTIDAS", "BURITACA", "MINCA"],
        "Nombre_nivel": ["Semestre 01", "Semestre 01", "Semestre 01", "Semestre 02", "Semestre 01"],
        "Nombre_modulo": ["MOD1", "MOD2", "MOD1", "MOD1", "MOD2"],
        "Seguimiento": ["Seguimiento 1", "Seguimiento 2", "Seguimiento 3", "Seguimiento 1", "Seguimiento 2"],
        "Grupo": ["A", "B", "A", "A", "B"],
        "Cantidad_inasistencia": [2, 3, 1, 5, 2],
        "Fecha_inasistencia": pd.to_datetime(["2026-02-10", "2026-04-15", "2026-05-01", "2026-03-01", "2026-05-20"]),
    })


@pytest.fixture
def df_notas_muestra():
    return pd.DataFrame({
        "Numero_identificacion_estudiante": ["1", "2", "3"],
        "Nombre_completo_estudiante": ["Ana", "Luis", "Eva"],
        "Nota final": [2.5, 4.0, 1.0],
        "Nombre_asignatura": ["INTRODUCCIÓN A LA LOGÍSTICA", "INTRODUCCIÓN AL MARKETING DIGITAL", "INGLÉS I"],
        "Codigo_asignatura": ["LOG101", "MKT101", "ING101"],
    })


@pytest.fixture
def df_estudiantes_muestra():
    return pd.DataFrame({
        "Numero_identificacion": ["1", "2", "3", "4"],
        "Nombre_programa_limpio": [
            "TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS",
            "TECNOLOGÍA EN MARKETING DIGITAL",
            "TECNOLOGÍA EN GESTIÓN DE PRODUCCIÓN DE MODAS",
            "TECNOLOGÍA EN GESTIÓN DE SERVICIOS GASTRONÓMICOS",
        ],
        "Sede": ["BASTIDAS", "MINCA", "INEM", "INEM"],
        "Nombre_nivel": ["Semestre 01", "Semestre 01", "Semestre 02", "Semestre 01"],
    })
