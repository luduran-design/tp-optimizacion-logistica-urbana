"""Tests de validaciones de constructor de Ventana."""

import pytest

from modelado import Ventana, DatosInvalidos


class TestValidacionVentana:
    def test_ventana_valida_construye(self):
        v = Ventana(10, 20)
        assert v.inicio == 10 and v.fin == 20

    def test_inicio_igual_a_fin_lanza_error(self):
        # Una ventana de duracion cero no tiene sentido.
        with pytest.raises(DatosInvalidos):
            Ventana(10, 10)

    def test_inicio_mayor_a_fin_lanza_error(self):
        with pytest.raises(DatosInvalidos):
            Ventana(20, 10)
