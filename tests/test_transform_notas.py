import pytest

from src.transform_notas import _extraer_seguimientos, _asignar_grupo, _calcular_nota_final, _limpiar_nombre_asignatura


class TestExtraerSeguimientos:

    def test_lista_vacia(self):
        assert _extraer_seguimientos([]) == {}

    def test_sin_parametros(self):
        assert _extraer_seguimientos(None) == {}

    def test_tres_padres_renombra(self):
        params = [
            {"Consecutivo_parametro": 1, "Nombre_parametro": "PRIMER CORTE", "Consecutivo_padre": None, "Nota": 4.2},
            {"Consecutivo_parametro": 2, "Nombre_parametro": "SEGUNDO CORTE", "Consecutivo_padre": None, "Nota": 3.6},
            {"Consecutivo_parametro": 3, "Nombre_parametro": "TERCER CORTE", "Consecutivo_padre": None, "Nota": None},
        ]
        esperado = {
            "Primer Seguimiento": 4.2,
            "Segundo Seguimiento": 3.6,
            "Tercer Seguimiento": None,
        }
        assert _extraer_seguimientos(params) == esperado

    def test_hijos_en_medio_ignora(self):
        params = [
            {"Consecutivo_parametro": 1, "Nombre_parametro": "Primer Seguimiento", "Consecutivo_padre": None, "Nota": 5.0},
            {"Consecutivo_parametro": 2, "Nombre_parametro": "Hijo", "Consecutivo_padre": 999, "Nota": 4.0},
            {"Consecutivo_parametro": 3, "Nombre_parametro": "Segundo Seguimiento", "Consecutivo_padre": None, "Nota": 3.0},
            {"Consecutivo_parametro": 4, "Nombre_parametro": "Tercer Seguimiento", "Consecutivo_padre": None, "Nota": 2.0},
        ]
        esperado = {
            "Primer Seguimiento": 5.0,
            "Segundo Seguimiento": 3.0,
            "Tercer Seguimiento": 2.0,
        }
        assert _extraer_seguimientos(params) == esperado

    def test_mas_de_tres_padres_ignora_resto(self):
        params = [
            {"Consecutivo_parametro": 1, "Nombre_parametro": "C1", "Consecutivo_padre": None, "Nota": 5.0},
            {"Consecutivo_parametro": 2, "Nombre_parametro": "C2", "Consecutivo_padre": None, "Nota": 4.0},
            {"Consecutivo_parametro": 3, "Nombre_parametro": "C3", "Consecutivo_padre": None, "Nota": 3.0},
            {"Consecutivo_parametro": 4, "Nombre_parametro": "C4", "Consecutivo_padre": None, "Nota": 2.0},
        ]
        esperado = {
            "Primer Seguimiento": 5.0,
            "Segundo Seguimiento": 4.0,
            "Tercer Seguimiento": 3.0,
        }
        assert _extraer_seguimientos(params) == esperado

    def test_menos_de_tres_padres(self):
        params = [
            {"Consecutivo_parametro": 1, "Nombre_parametro": "Unico", "Consecutivo_padre": None, "Nota": 4.0},
        ]
        assert _extraer_seguimientos(params) == {"Primer Seguimiento": 4.0}


class TestAsignarGrupo:

    def test_con_sufijo_1(self):
        assert _asignar_grupo("CURSO (1)") == "1"

    def test_con_sufijo_A(self):
        assert _asignar_grupo("CURSO (A)") == "A"

    def test_sin_sufijo(self):
        assert _asignar_grupo("CURSO") == "A"

    def test_nulo(self):
        assert _asignar_grupo(None) == "A"

    def test_vacio(self):
        assert _asignar_grupo("") == "A"


class TestCalcularNotaFinal:

    def test_notas_completas_grupo_a(self):
        row = {"Primer Seguimiento": 4.0, "Segundo Seguimiento": 3.0, "Tercer Seguimiento": 5.0}
        assert _calcular_nota_final(row, "A") == pytest.approx(4.0 * 0.3 + 3.0 * 0.3 + 5.0 * 0.4)

    def test_notas_none_grupo_a(self):
        row = {"Primer Seguimiento": None, "Segundo Seguimiento": None, "Tercer Seguimiento": None}
        assert _calcular_nota_final(row, "A") == 0.0

    def test_notas_parciales_grupo_a(self):
        row = {"Primer Seguimiento": 4.0, "Segundo Seguimiento": None, "Tercer Seguimiento": 5.0}
        assert _calcular_nota_final(row, "A") == pytest.approx(4.0 * 0.3 + 0 + 5.0 * 0.4)

    def test_grupo_b_solo_primer(self):
        row = {"Primer Seguimiento": 4.5, "Segundo Seguimiento": 3.0, "Tercer Seguimiento": 5.0}
        assert _calcular_nota_final(row, "B") == 4.5


class TestLimpiarNombreAsignatura:

    def test_quita_prefijo(self):
        assert _limpiar_nombre_asignatura("42040107-GESTIÓN NAVIERA Y PORTUARIA", "42040107") == "GESTIÓN NAVIERA Y PORTUARIA"

    def test_sin_prefijo(self):
        assert _limpiar_nombre_asignatura("COMUNICACIÓN ESCRITA", "XYZ") == "COMUNICACIÓN ESCRITA"

    def test_nombre_nulo(self):
        assert _limpiar_nombre_asignatura(None, "123") is None

    def test_codigo_nulo(self):
        assert _limpiar_nombre_asignatura("ALGO", None) == "ALGO"
