import pandas as pd
import pytest

from src.reporte_bajo_rendimiento import _asignar_area, _tabla_agrupada


class TestAsignarArea:

    def test_logistica(self):
        assert _asignar_area("GESTIÓN NAVIERA Y PORTUARIA") == "Logistica y Comercio"

    def test_marketing(self):
        assert _asignar_area("INTRODUCCIÓN AL MARKETING DIGITAL") == "Marketing y Ventas"

    def test_turismo(self):
        assert _asignar_area("FUNDAMENTOS DE LA OPERACIÓN TURÍSTICA") == "Turismo"

    def test_modas(self):
        assert _asignar_area("PATRONAJE Y ESCALADO") == "Diseno y Modas"

    def test_gastronomia(self):
        assert _asignar_area("GASTRONOMÍA I") == "Gastronomia"

    def test_sin_acento_coincide(self):
        assert _asignar_area("GESTION NAVIERA Y PORTUARIA") == "Logistica y Comercio"

    def test_desconocido(self):
        assert _asignar_area("ASIGNATURA INVENTADA") == "Otra"

    def test_nulo(self):
        assert _asignar_area(None) == "Otra"


class TestTablas:

    @pytest.fixture
    def df(self):
        df = pd.DataFrame({
            "Nota final": [4.5, 2.0, 0.5, 3.5, 1.0],
            "Nombre_asignatura": ["MATE", "HISTORIA", "MATE", "LENGUA", "HISTORIA"],
            "Codigo_asignatura": ["M01", "H01", "M01", "L01", "H01"],
            "Area": ["Matematicas y Estadistica", "Comunicacion", "Matematicas y Estadistica", "Comunicacion", "Comunicacion"],
            "Nombre_curso": ["CURSO A", "CURSO B", "CURSO A", "CURSO C", "CURSO B"],
            "Sede": ["SEDE1", "SEDE2", "SEDE1", "SEDE1", "SEDE2"],
            "Nombre_programa_limpio": ["PROG1", "PROG2", "PROG1", "PROG1", "PROG2"],
            "Numero_identificacion_estudiante": [1, 2, 3, 4, 5],
            "Nombre_completo_estudiante": ["A", "B", "C", "D", "E"],
        })
        df["bajo"] = (df["Nota final"] < 3.0) & (df["Nota final"] > 1)
        df["condicion_de_alerta"] = (df["Nota final"] <= 1) & (df["Nota final"] >= 0)
        return df

    def test_tabla_area(self, df):
        res = _tabla_agrupada(df, ["Area"])
        assert "Area" in res.columns
        assert "Porcentaje_bajo" in res.columns
        assert len(res) == 2

    def test_tabla_asignatura(self, df):
        res = _tabla_agrupada(df, ["Codigo_asignatura", "Nombre_asignatura", "Area"])
        assert "Codigo_asignatura" in res.columns
        assert len(res) == 3

    def test_tabla_curso(self, df):
        res = _tabla_agrupada(df, ["Nombre_curso", "Sede", "Nombre_programa_limpio", "Area"])
        assert "Nombre_curso" in res.columns
        assert len(res) == 3

    def test_tabla_estudiantes_revision(self, df):
        res = df[df["condicion_de_alerta"]][
            ["Nombre_completo_estudiante", "Numero_identificacion_estudiante", "Sede", "Nombre_programa_limpio", "Nombre_asignatura", "Nota final"]
        ].drop_duplicates().reset_index(drop=True)
        assert len(res) == 2
