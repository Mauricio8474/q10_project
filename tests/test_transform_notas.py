import pytest

from src.transform_notas import _extraer_seguimientos


class TestExtraerSeguimientos:

    def test_lista_vacia(self):
        assert _extraer_seguimientos([]) == {}

    def test_sin_parametros(self):
        assert _extraer_seguimientos(None) == {}

    def test_tres_parametros(self):
        params = [
            {"Consecutivo_parametro": 1, "Nombre_parametro": "PRIMER CORTE", "Nota": 4.2},
            {"Consecutivo_parametro": 2, "Nombre_parametro": "SEGUNDO CORTE", "Nota": 3.6},
            {"Consecutivo_parametro": 3, "Nombre_parametro": "TERCER CORTE", "Nota": None},
        ]
        esperado = {
            "Primer Seguimiento": 4.2,
            "Segundo Seguimiento": 3.6,
            "Tercer Seguimiento": None,
        }
        assert _extraer_seguimientos(params) == esperado

    def test_mas_de_tres_parametros_ignora_resto(self):
        params = [
            {"Consecutivo_parametro": 1, "Nombre_parametro": "Corte 1", "Nota": 5.0},
            {"Consecutivo_parametro": 2, "Nombre_parametro": "Corte 2", "Nota": 4.0},
            {"Consecutivo_parametro": 3, "Nombre_parametro": "Corte 3", "Nota": 3.0},
            {"Consecutivo_parametro": 4, "Nombre_parametro": "Extra", "Nota": 2.0},
        ]
        esperado = {
            "Primer Seguimiento": 5.0,
            "Segundo Seguimiento": 4.0,
            "Tercer Seguimiento": 3.0,
        }
        assert _extraer_seguimientos(params) == esperado

    def test_menos_de_tres_parametros(self):
        params = [
            {"Consecutivo_parametro": 1, "Nombre_parametro": "Único", "Nota": 4.0},
        ]
        esperado = {
            "Primer Seguimiento": 4.0,
        }
        assert _extraer_seguimientos(params) == esperado
