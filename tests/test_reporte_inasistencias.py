import pandas as pd
import pytest

from src.reporte_inasistencias import _agrupar_inasistencias, _cruzada


class TestAgruparInasistencias:

    def test_return_type(self, df_inasistencias_muestra):
        res = _agrupar_inasistencias(df_inasistencias_muestra, ["Sede"])
        assert isinstance(res, pd.DataFrame)

    def test_columnas_esperadas(self, df_inasistencias_muestra):
        res = _agrupar_inasistencias(df_inasistencias_muestra, ["Sede"])
        assert "Sede" in res.columns
        assert "Total_estudiantes" in res.columns
        assert "Total_inasistencias" in res.columns
        assert "Promedio_inasistencias" in res.columns

    def test_agrupa_sede(self, df_inasistencias_muestra):
        res = _agrupar_inasistencias(df_inasistencias_muestra, ["Sede"])
        # 3 sedes: BASTIDAS, MINCA, BURITACA
        assert len(res) == 3

    def test_agrupa_programa(self, df_inasistencias_muestra):
        res = _agrupar_inasistencias(
            df_inasistencias_muestra, ["Nombre_programa_limpio"]
        )
        assert len(res) == 2

    def test_valores_correctos(self, df_inasistencias_muestra):
        res = _agrupar_inasistencias(
            df_inasistencias_muestra, ["Nombre_programa_limpio"]
        )
        fila = res[res["Nombre_programa_limpio"].str.contains("LOGÍSTICAS", na=False)]
        assert fila["Total_estudiantes"].values[0] == 2
        assert fila["Total_inasistencias"].values[0] == 8

    def test_dataframe_vacio(self):
        df_vacio = pd.DataFrame(columns=["Sede", "Cantidad_inasistencia", "Numero_identificacion_estudiante"])
        res = _agrupar_inasistencias(df_vacio, ["Sede"])
        assert len(res) == 0


class TestCruzada:

    def test_return_type(self, df_inasistencias_muestra):
        res = _cruzada(df_inasistencias_muestra, "Sede")
        assert isinstance(res, pd.DataFrame)

    def test_tiene_seguimientos(self, df_inasistencias_muestra):
        res = _cruzada(df_inasistencias_muestra, "Sede")
        for seg in ["Seguimiento 1", "Seguimiento 2", "Seguimiento 3"]:
            assert seg in res.columns

    def test_valores(self, df_inasistencias_muestra):
        res = _cruzada(df_inasistencias_muestra, "Sede")
        # BASTIDAS: Seg 1=1, Seg 2=0, Seg 3=1
        bastidas = res[res["Sede"] == "BASTIDAS"]
        assert bastidas["Seguimiento 1"].values[0] == 1
        assert bastidas["Seguimiento 3"].values[0] == 1
