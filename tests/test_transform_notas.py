import pytest

from src.transform_notas import _es_hoja, _extraer_parametros_hoja


class TestEsHoja:

    def test_parametro_sin_padres_es_hoja(self):
        padres = {100, 200}
        parametro = {"Consecutivo_parametro": 300}
        assert _es_hoja(parametro, padres) is True

    def test_parametro_que_es_padre_no_es_hoja(self):
        padres = {100, 200}
        parametro = {"Consecutivo_parametro": 100}
        assert _es_hoja(parametro, padres) is False


class TestExtraerParametrosHoja:

    def test_lista_vacia(self):
        assert _extraer_parametros_hoja([]) == {}

    def test_sin_parametros(self):
        assert _extraer_parametros_hoja(None) == {}

    def test_solo_hojas(self):
        params = [
            {"Consecutivo_parametro": 1, "Nombre_parametro": "Tarea 1", "Nota": 4.5},
            {"Consecutivo_parametro": 2, "Nombre_parametro": "Tarea 2", "Nota": 3.0},
        ]
        assert _extraer_parametros_hoja(params) == {"Tarea 1": 4.5, "Tarea 2": 3.0}

    def test_jerarquico_solo_hojas(self):
        params = [
            {"Consecutivo_parametro": 10, "Nombre_parametro": "Tareas", "Nota": None, "Consecutivo_padre": None},
            {"Consecutivo_parametro": 11, "Nombre_parametro": "Tarea 1", "Nota": 4.0, "Consecutivo_padre": 10},
            {"Consecutivo_parametro": 12, "Nombre_parametro": "Tarea 2", "Nota": 3.5, "Consecutivo_padre": 10},
        ]
        assert _extraer_parametros_hoja(params) == {"Tarea 1": 4.0, "Tarea 2": 3.5}

    def test_nota_none_se_incluye(self):
        params = [
            {"Consecutivo_parametro": 1, "Nombre_parametro": "Parcial", "Nota": None},
        ]
        result = _extraer_parametros_hoja(params)
        assert result == {"Parcial": None}
