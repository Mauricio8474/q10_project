import pandas as pd
import pytest

from src.analisis_inasistencias import (
    _asignar_grupo_estudiante,
    _clasificar_seguimiento,
)


class TestAsignarGrupoEstudiante:

    def test_moda_inem_semestre_1(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN GESTIÓN DE PRODUCCIÓN DE MODAS", "INEM", "Semestre 01"
        ) == "B"

    def test_moda_inem_semestre_2(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN GESTIÓN DE PRODUCCIÓN DE MODAS", "INEM", "Semestre 02"
        ) == "A"

    def test_moda_otra_sede_semestre_1(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN GESTIÓN DE PRODUCCIÓN DE MODAS", "BASTIDAS", "Semestre 01"
        ) == "A"

    def test_logistica_semestre_1(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS", "BASTIDAS", "Semestre 01"
        ) == "B"

    def test_marketing_semestre_1(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN MARKETING DIGITAL", "BASTIDAS", "Semestre 01"
        ) == "B"

    def test_logistica_semestre_2(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS", "BASTIDAS", "Semestre 02"
        ) == "A"

    def test_otro_programa_semestre_1(self):
        assert _asignar_grupo_estudiante(
            "OTRO PROGRAMA", "MINCA", "Semestre 01"
        ) == "A"

    def test_none(self):
        assert _asignar_grupo_estudiante(None, None, None) == "A"

    def test_nan_float(self):
        assert _asignar_grupo_estudiante(float("nan"), float("nan"), float("nan")) == "A"

    def test_nan_nivel(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN GESTIÓN DE PRODUCCIÓN DE MODAS", "INEM", float("nan")
        ) == "A"


class TestClasificarSeguimiento:

    def test_grupo_a_seg1(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-02-15"), "A") == "Seguimiento 1"

    def test_grupo_a_seg2(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-03-20"), "A") == "Seguimiento 2"

    def test_grupo_a_seg3(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-04-25"), "A") == "Seguimiento 3"

    def test_grupo_a_fuera_rango(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-06-01"), "A") is None

    def test_grupo_b_seg1(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-04-10"), "B") == "Seguimiento 1"

    def test_grupo_b_seg2(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-05-15"), "B") == "Seguimiento 2"

    def test_grupo_b_seg3(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-06-20"), "B") == "Seguimiento 3"

    def test_grupo_b_fuera_rango(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-08-01"), "B") is None

    def test_borde_exacto_inicio(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-02-01"), "A") == "Seguimiento 1"

    def test_borde_exacto_corte(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-03-15"), "A") == "Seguimiento 2"
