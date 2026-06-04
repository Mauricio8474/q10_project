import pandas as pd
import pytest

from src.consolidar import _separar_sede_programa


class TestSepararSedePrograma:

    def test_formato_estandar(self):
        sede, prog = _separar_sede_programa("BASTIDAS - TECNOLOGÍA EN MARKETING DIGITAL")
        assert sede == "BASTIDAS"
        assert prog == "TECNOLOGÍA EN MARKETING DIGITAL"

    def test_con_tres_partes(self):
        sede, prog = _separar_sede_programa("INEM - Principal - TECNOLOGÍA EN DATOS")
        assert sede == "INEM"
        assert prog == "TECNOLOGÍA EN DATOS"

    def test_sin_guion(self):
        sede, prog = _separar_sede_programa("SOLO PROGRAMA")
        assert sede == "SOLO PROGRAMA"
        assert prog == ""

    def test_nulo(self):
        sede, prog = _separar_sede_programa(None)
        assert sede == ""
        assert prog == ""

    def test_vacio(self):
        sede, prog = _separar_sede_programa("")
        assert sede == ""
        assert prog == ""
