from datetime import date
from unittest.mock import patch

import pytest

from src.extract_edades import calcular_edad


class TestCalcularEdad:

    def test_fecha_valida(self):
        with patch("src.extract_edades.date") as mock_date:
            mock_date.today.return_value = date(2026, 6, 1)
            mock_date.fromisoformat = date.fromisoformat
            assert calcular_edad("2000-01-15") == 26

    def test_fecha_con_formato_iso_completo(self):
        with patch("src.extract_edades.date") as mock_date:
            mock_date.today.return_value = date(2026, 6, 1)
            mock_date.fromisoformat = date.fromisoformat
            assert calcular_edad("2000-01-15T00:00:00") == 26

    def test_cumpleanos_aun_no(self):
        with patch("src.extract_edades.date") as mock_date:
            mock_date.today.return_value = date(2026, 6, 1)
            mock_date.fromisoformat = date.fromisoformat
            assert calcular_edad("2000-07-01") == 25

    def test_cumpleanos_hoy(self):
        with patch("src.extract_edades.date") as mock_date:
            mock_date.today.return_value = date(2026, 6, 1)
            mock_date.fromisoformat = date.fromisoformat
            assert calcular_edad("2000-06-01") == 26

    def test_fecha_vacia_retorna_none(self):
        assert calcular_edad("") is None

    def test_fecha_none_retorna_none(self):
        assert calcular_edad(None) is None

    def test_fecha_invalida_retorna_none(self):
        assert calcular_edad("no-es-una-fecha") is None
