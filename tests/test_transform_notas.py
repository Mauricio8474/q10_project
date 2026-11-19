import pandas as pd
import pytest

from src import transform_notas
from src.transform_notas import (
    _extraer_seguimientos,
    _asignar_grupo,
    _calcular_nota_final,
    _extraer_semestre,
    _asignar_calendario,
    _limpiar_nombre_asignatura,
    transformar_notas,
)


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

    def test_notas_completas(self):
        row = {"Primer Seguimiento": 4.0, "Segundo Seguimiento": 3.0, "Tercer Seguimiento": 5.0}
        assert _calcular_nota_final(row) == pytest.approx(4.0 * 0.3 + 3.0 * 0.3 + 5.0 * 0.4)

    def test_notas_none(self):
        row = {"Primer Seguimiento": None, "Segundo Seguimiento": None, "Tercer Seguimiento": None}
        assert _calcular_nota_final(row) == 0.0

    def test_notas_parciales(self):
        row = {"Primer Seguimiento": 4.0, "Segundo Seguimiento": None, "Tercer Seguimiento": 5.0}
        assert _calcular_nota_final(row) == pytest.approx(4.0 * 0.3 + 0 + 5.0 * 0.4)


class TestExtraerSemestre:

    def test_codigo_numerico_sem_01(self):
        assert _extraer_semestre("42010101") == "01"

    def test_codigo_numerico_sem_02(self):
        assert _extraer_semestre("42050207") == "02"

    def test_codigo_corto(self):
        assert _extraer_semestre("12345") is None

    def test_codigo_no_numerico(self):
        assert _extraer_semestre("TecLab-001") is None

    def test_codigo_none(self):
        assert _extraer_semestre(None) is None


class TestAsignarCalendario:
    """
    CALENDARIO_2_PROGRAMAS_MODA/TURISMO_MARKETING vienen de semestre.json y
    cambian cada periodo (p.ej. vacíos en el periodo 7). Se monkeypatchean
    para que estos tests no dependan del contenido actual del archivo.
    """

    def test_moda_inem(self, monkeypatch):
        monkeypatch.setattr(transform_notas, "CALENDARIO_2_PROGRAMAS_MODA", ["Tecnolog-Mod-Inem"])
        assert _asignar_calendario("Tecnolog-Mod-Inem", "42050101") == 2

    def test_turismo_minca_sem_01(self, monkeypatch):
        monkeypatch.setattr(transform_notas, "CALENDARIO_2_PROGRAMAS_TURISMO_MARKETING", ["Tecnolog-Turis-Min"])
        assert _asignar_calendario("Tecnolog-Turis-Min", "42020101") == 2

    def test_turismo_minca_sem_02(self, monkeypatch):
        monkeypatch.setattr(transform_notas, "CALENDARIO_2_PROGRAMAS_TURISMO_MARKETING", ["Tecnolog-Turis-Min"])
        assert _asignar_calendario("Tecnolog-Turis-Min", "42020208") == 1

    def test_turismo_buritaca_sem_01(self, monkeypatch):
        monkeypatch.setattr(transform_notas, "CALENDARIO_2_PROGRAMAS_TURISMO_MARKETING", ["Tecnolog-Turis-Bur"])
        assert _asignar_calendario("Tecnolog-Turis-Bur", "42020101") == 2

    def test_marketing_minca_sem_01(self, monkeypatch):
        monkeypatch.setattr(transform_notas, "CALENDARIO_2_PROGRAMAS_TURISMO_MARKETING", ["Tecnolog-Mkt-Min"])
        assert _asignar_calendario("Tecnolog-Mkt-Min", "42010101") == 2

    def test_marketing_buritaca_sem_01(self, monkeypatch):
        monkeypatch.setattr(transform_notas, "CALENDARIO_2_PROGRAMAS_TURISMO_MARKETING", ["Tecnolog-Mkt-Bur"])
        assert _asignar_calendario("Tecnolog-Mkt-Bur", "42010101") == 2

    def test_marketing_minca_sem_02(self, monkeypatch):
        monkeypatch.setattr(transform_notas, "CALENDARIO_2_PROGRAMAS_TURISMO_MARKETING", ["Tecnolog-Mkt-Min"])
        assert _asignar_calendario("Tecnolog-Mkt-Min", "42010208") == 1

    def test_gastronomia_sem_01(self):
        assert _asignar_calendario("Tecnolog-Gastro", "42030101") == 1

    def test_logistica_sem_01(self):
        assert _asignar_calendario("Tecnolog-Logis", "42040101") == 1

    def test_periodo_sin_calendario_2_todo_es_1(self, monkeypatch):
        monkeypatch.setattr(transform_notas, "CALENDARIO_2_PROGRAMAS_MODA", [])
        monkeypatch.setattr(transform_notas, "CALENDARIO_2_PROGRAMAS_TURISMO_MARKETING", [])
        assert _asignar_calendario("Tecnolog-Mod-Inem", "42050101") == 1
        assert _asignar_calendario("Tecnolog-Turis-Min", "42020101") == 1


class TestLimpiarNombreAsignatura:

    def test_quita_prefijo(self):
        assert _limpiar_nombre_asignatura("42040107-GESTIÓN NAVIERA Y PORTUARIA", "42040107") == "GESTIÓN NAVIERA Y PORTUARIA"

    def test_sin_prefijo(self):
        assert _limpiar_nombre_asignatura("COMUNICACIÓN ESCRITA", "XYZ") == "COMUNICACIÓN ESCRITA"

    def test_nombre_nulo(self):
        assert _limpiar_nombre_asignatura(None, "123") is None

    def test_codigo_nulo(self):
        assert _limpiar_nombre_asignatura("ALGO", None) == "ALGO"


class TestTransformarNotasCreditos:
    """
    transformar_notas() agrega Creditos_asignatura desde data/raw/pensum.parquet
    (join por Codigo_programa + Codigo_asignatura). Se monkeypatchean el I/O
    y la config de calendario/exclusión para no depender del estado real del repo.
    """

    def _df_raw_minimo(self):
        params = [
            {"Consecutivo_padre": None, "Nota": 4.0},
            {"Consecutivo_padre": None, "Nota": 3.0},
            {"Consecutivo_padre": None, "Nota": 5.0},
        ]
        return pd.DataFrame({
            "Nombre_curso": ["CURSO X (A)"],
            "Nombre_programa": ["BASTIDAS - TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS"],
            "Codigo_programa": ["Tecnolog-Logis-Bas"],
            "Codigo_asignatura": ["42040101"],
            "Nombre_asignatura": ["42040101-COMUNICACIÓN ESCRITA"],
            "Parametros_evaluacion": [params],
        })

    def _preparar_monkeypatch(self, monkeypatch):
        monkeypatch.setattr(transform_notas, "EXCLUIR_PROGRAMAS", [])
        monkeypatch.setattr(transform_notas, "CALENDARIO_2_PROGRAMAS_MODA", [])
        monkeypatch.setattr(transform_notas, "CALENDARIO_2_PROGRAMAS_TURISMO_MARKETING", [])
        monkeypatch.setattr(transform_notas, "guardar_parquet", lambda *a, **k: None)
        monkeypatch.setattr(transform_notas, "guardar_csv", lambda *a, **k: None)

    def test_agrega_creditos_cuando_hay_pensum(self, monkeypatch):
        self._preparar_monkeypatch(monkeypatch)
        pensum = pd.DataFrame({
            "Codigo_programa": ["Tecnolog-Logis-Bas"],
            "Codigo_asignatura": ["42040101"],
            "Creditos_asignatura": [2.0],
        })
        monkeypatch.setattr(transform_notas.pd, "read_parquet", lambda *a, **k: pensum)

        df = transformar_notas(self._df_raw_minimo())

        assert df.loc[0, "Creditos_asignatura"] == 2.0

    def test_sin_pensum_no_falla(self, monkeypatch):
        self._preparar_monkeypatch(monkeypatch)

        def _raise(*a, **k):
            raise FileNotFoundError

        monkeypatch.setattr(transform_notas.pd, "read_parquet", _raise)

        df = transformar_notas(self._df_raw_minimo())

        assert "Creditos_asignatura" not in df.columns
