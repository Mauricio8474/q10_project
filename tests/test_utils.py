import re

import pandas as pd
import pytest

from src.utils import limpiar_columnas, fecha_actual


class TestLimpiarColumnas:

    def test_columnas_a_minusculas_sin_espacios(self):
        df = pd.DataFrame(columns=["Nombre Completo", "Edad "])
        resultado = limpiar_columnas(df)
        assert list(resultado.columns) == ["nombre_completo", "edad"]

    def test_dataframe_vacio_con_columnas(self):
        df = pd.DataFrame(columns=["A ", " B"])
        resultado = limpiar_columnas(df)
        assert list(resultado.columns) == ["a", "b"]


class TestFechaActual:

    def test_formato_correcto(self):
        fecha = fecha_actual()
        assert re.match(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", fecha)
