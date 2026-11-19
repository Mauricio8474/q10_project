import re

import pandas as pd
import pytest

from src.utils import limpiar_columnas, fecha_actual, separar_sede_programa


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


class TestSepararSedePrograma:

    def test_formato_estandar(self):
        sede, prog = separar_sede_programa("INEM - TARDE - TECNOLOGÍA EN GESTIÓN DE SISTEMAS ELÉCTRICOS")
        assert sede == "INEM"
        assert prog == "TECNOLOGÍA EN GESTIÓN DE SISTEMAS ELÉCTRICOS"

    def test_dos_partes(self):
        sede, prog = separar_sede_programa("PESCAITO - TECNOLOGÍA EN GESTIÓN DE SERVICIOS GASTRONÓMICOS")
        assert sede == "PESCAITO"
        assert prog == "TECNOLOGÍA EN GESTIÓN DE SERVICIOS GASTRONÓMICOS"

    def test_sin_guion(self):
        sede, prog = separar_sede_programa("SOLO PROGRAMA")
        assert sede == "SOLO PROGRAMA"
        assert prog == ""

    def test_nulo(self):
        sede, prog = separar_sede_programa(None)
        assert sede == ""
        assert prog == ""

    def test_vacio(self):
        sede, prog = separar_sede_programa("")
        assert sede == ""
        assert prog == ""


class TestRequestWithRetry:

    def test_retorna_none_si_siempre_falla(self):
        import requests
        from src.utils import request_with_retry

        def _siempre_errores(*args, **kwargs):
            raise requests.ConnectionError("Simulado")

        resultado = request_with_retry(_siempre_errores, max_retries=2, delay=0.01)
        assert resultado is None
