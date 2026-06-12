import pandas as pd
import pytest

from src.analisis_inasistencias import (
    _asignar_grupo_estudiante,
    _clasificar_seguimiento,
    enriquecer_inasistencias,
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

    def test_logistica_minca_semestre_1(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS", "MINCA", "Semestre 01"
        ) == "B"

    def test_logistica_buritaca_semestre_1(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS", "BURITACA", "Semestre 01"
        ) == "B"

    def test_logistica_bastidas_semestre_1(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS", "BASTIDAS", "Semestre 01"
        ) == "A"

    def test_marketing_minca_semestre_1(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN MARKETING DIGITAL", "MINCA", "Semestre 01"
        ) == "B"

    def test_marketing_buritaca_semestre_1(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN MARKETING DIGITAL", "BURITACA", "Semestre 01"
        ) == "B"

    def test_marketing_bastidas_semestre_1(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN MARKETING DIGITAL", "BASTIDAS", "Semestre 01"
        ) == "A"

    def test_logistica_minca_semestre_2(self):
        assert _asignar_grupo_estudiante(
            "TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS", "MINCA", "Semestre 02"
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


class TestEnriquecerInasistencias:

    def test_filtra_sin_programa(self):
        detalle = pd.DataFrame({
            "Numero_identificacion_estudiante": ["1", "2", "3"],
            "Fecha_inasistencia": pd.to_datetime(["2026-02-10", "2026-03-15", "2026-04-20"]),
            "Cantidad_inasistencia": [2, 3, 1],
            "Nombre_modulo": ["MOD1", "MOD2", "MOD1"],
        })
        estudiantes = pd.DataFrame({
            "Numero_identificacion": ["1", "2", "3"],
            "Nombre_programa_limpio": [None, "TECNOLOGÍA EN MARKETING DIGITAL", "TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS"],
            "Sede": [None, "MINCA", "BASTIDAS"],
            "Nombre_nivel": [None, "Semestre 01", "Semestre 01"],
        })
        res = enriquecer_inasistencias(detalle, estudiantes)
        # Estudiante 1 sin programa debe ser filtrado
        assert len(res) == 2
        assert "MINCA" in res["Sede"].values

    def test_grupo_asignado(self):
        detalle = pd.DataFrame({
            "Numero_identificacion_estudiante": ["1"],
            "Fecha_inasistencia": pd.to_datetime(["2026-04-15"]),
            "Cantidad_inasistencia": [2],
            "Nombre_modulo": ["MOD1"],
        })
        estudiantes = pd.DataFrame({
            "Numero_identificacion": ["1"],
            "Nombre_programa_limpio": ["TECNOLOGÍA EN MARKETING DIGITAL"],
            "Sede": ["MINCA"],
            "Nombre_nivel": ["Semestre 01"],
        })
        res = enriquecer_inasistencias(detalle, estudiantes)
        assert res["Grupo"].values[0] == "B"

    def test_seguimiento_asignado(self):
        detalle = pd.DataFrame({
            "Numero_identificacion_estudiante": ["1"],
            "Fecha_inasistencia": pd.to_datetime(["2026-02-15"]),
            "Cantidad_inasistencia": [1],
            "Nombre_modulo": ["MOD1"],
        })
        estudiantes = pd.DataFrame({
            "Numero_identificacion": ["1"],
            "Nombre_programa_limpio": ["TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS"],
            "Sede": ["BASTIDAS"],
            "Nombre_nivel": ["Semestre 01"],
        })
        res = enriquecer_inasistencias(detalle, estudiantes)
        assert res["Seguimiento"].values[0] == "Seguimiento 1"

    def test_sin_estudiantes_retorna_vacio(self):
        detalle = pd.DataFrame({
            "Numero_identificacion_estudiante": ["1"],
            "Fecha_inasistencia": pd.to_datetime(["2026-02-15"]),
            "Cantidad_inasistencia": [1],
            "Nombre_modulo": ["MOD1"],
        })
        estudiantes = pd.DataFrame(columns=[
            "Numero_identificacion", "Nombre_programa_limpio", "Sede", "Nombre_nivel"
        ])
        res = enriquecer_inasistencias(detalle, estudiantes)
        assert len(res) == 0
