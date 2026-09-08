"""Tests de validacion de Parada (enum ResultadoParada)."""

import pytest

from modelado import Parada, ResultadoParada, DatosInvalidos
from tests.helpers import _solicitud_basica


class TestEnumParada:
    def test_resultado_valido_construye(self):
        p = Parada(1, _solicitud_basica(), 10, ResultadoParada.ENTREGADA)
        assert p.resultado == ResultadoParada.ENTREGADA

    def test_resultado_string_libre_lanza_error(self):
        # Antes: aceptaba "CANCELADA" sin chistar. Ahora rechaza.
        with pytest.raises(DatosInvalidos, match="ResultadoParada"):
            Parada(1, _solicitud_basica(), 10, "CANCELADA")

    def test_resultado_none_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="ResultadoParada"):
            Parada(1, _solicitud_basica(), 10, None)
