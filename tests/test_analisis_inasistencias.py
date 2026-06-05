import pandas as pd
import pytest

from src.analisis_inasistencias import (
    _asignar_grupo_estudiante,
    _clasificar_seguimiento,
)


class TestAsignarGrupoEstudiante:

    def test_programa_grupo_b(self):
        assert _asignar_grupo_estudiante("TECNOLOGÍA EN GESTIÓN DE PRODUCCIÓN DE MODAS", "INEM") == "B"

    def test_sede_grupo_b(self):
        assert _asignar_grupo_estudiante("OTRO PROGRAMA", "MINCA") == "B"

    def test_sede_buritaca(self):
        assert _asignar_grupo_estudiante("OTRO PROGRAMA", "BURITACA") == "B"

    def test_grupo_a(self):
        assert _asignar_grupo_estudiante("TECNOLOGÍA EN MARKETING DIGITAL", "BASTIDAS") == "A"

    def test_none(self):
        assert _asignar_grupo_estudiante(None, None) == "A"

    def test_solo_programa_b(self):
        assert _asignar_grupo_estudiante("TECNOLOGÍA EN GESTIÓN DE PRODUCCIÓN DE MODAS", "BASTIDAS") == "B"


class TestClasificarSeguimiento:

    def test_grupo_a_seg1(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-02-15"), "A") == "Seguimiento 1 (01 Feb – 01 Abr)"

    def test_grupo_a_seg2(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-04-10"), "A") == "Seguimiento 2 (02 Abr – 13 May)"

    def test_grupo_a_seg3(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-05-20"), "A") == "Seguimiento 3 (14 May – 25 Jun)"

    def test_grupo_a_fuera_rango(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-07-01"), "A") is None

    def test_grupo_b_seg1(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-04-10"), "B") == "Seguimiento 1 (06 Abr – 09 May)"

    def test_grupo_b_seg2(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-05-15"), "B") == "Seguimiento 2 (10 May – 13 Jun)"

    def test_grupo_b_seg3(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-06-20"), "B") == "Seguimiento 3 (14 Jun – 25 Jul)"

    def test_borde_exacto_inicio(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-02-01"), "A") == "Seguimiento 1 (01 Feb – 01 Abr)"

    def test_borde_exacto_corte(self):
        assert _clasificar_seguimiento(pd.Timestamp("2026-04-02"), "A") == "Seguimiento 2 (02 Abr – 13 May)"
