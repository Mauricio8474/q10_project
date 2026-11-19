from src.extract_pensum import _aplanar_pensum


class TestAplanarPensum:

    def test_filas_del_pensum_actual(self):
        data = {
            "Codigo_programa": "Tecnolog-Logis-Bas",
            "Nombre_programa": "BASTIDAS - TECNOLOGÍA EN GESTIÓN DE OPERACIONES LOGÍSTICAS",
            "Pensum": [
                {
                    "Consecutivo_pensum_programa": 22,
                    "Nombre_pensum_programa": "Tecnolog-Logis-Bast-2025-2",
                    "Pensum_actual": True,
                    "Asignaturas": [
                        {
                            "Codigo_asignatura": "42040101",
                            "Nombre_asignatura": "42040101-COMUNICACIÓN ESCRITA",
                            "Abreviacion_asignatura": "ComEsc",
                            "Codigo_nivel": "01",
                            "Nombre_nivel": "Semestre 01",
                            "Intensidad_horaria_semanal": 2.0,
                            "Intensidad_horaria_total": 32.0,
                            "Creditos_asignatura": 2.0,
                        }
                    ],
                }
            ],
        }

        filas = _aplanar_pensum(data)

        assert len(filas) == 1
        assert filas[0]["Codigo_programa"] == "Tecnolog-Logis-Bas"
        assert filas[0]["Codigo_asignatura"] == "42040101"
        assert filas[0]["Creditos_asignatura"] == 2.0
        assert filas[0]["Consecutivo_pensum_programa"] == 22

    def test_ignora_pensums_no_actuales(self):
        data = {
            "Codigo_programa": "Tecnolog-Mkt-Bas",
            "Nombre_programa": "Marketing",
            "Pensum": [
                {
                    "Consecutivo_pensum_programa": 10,
                    "Pensum_actual": False,
                    "Asignaturas": [{"Codigo_asignatura": "001", "Creditos_asignatura": 3.0}],
                },
                {
                    "Consecutivo_pensum_programa": 11,
                    "Pensum_actual": True,
                    "Asignaturas": [{"Codigo_asignatura": "002", "Creditos_asignatura": 4.0}],
                },
            ],
        }

        filas = _aplanar_pensum(data)

        assert len(filas) == 1
        assert filas[0]["Codigo_asignatura"] == "002"
        assert filas[0]["Consecutivo_pensum_programa"] == 11

    def test_data_none_retorna_lista_vacia(self):
        assert _aplanar_pensum(None) == []

    def test_sin_pensum_retorna_lista_vacia(self):
        assert _aplanar_pensum({"Codigo_programa": "X", "Pensum": []}) == []

    def test_pensum_sin_asignaturas(self):
        data = {
            "Codigo_programa": "X",
            "Pensum": [{"Consecutivo_pensum_programa": 1, "Pensum_actual": True, "Asignaturas": []}],
        }
        assert _aplanar_pensum(data) == []
