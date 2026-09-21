"""Tests de Comprobante: validaciones en __init__ y guardado de atributos."""

import pytest

from modelado import Comprobante, DatosInvalidos
from tests.helpers import _solicitud_basica


class TestValidacionComprobante:
    """Regla 11: un comprobante tiene solicitud, fecha y hora reales, y
    receptor no vacio. Comprobante valida sus datos en el __init__ (checklist)."""

    def test_receptor_vacio_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="receptor"):
            Comprobante(1, _solicitud_basica(), 30, "")

    def test_receptor_none_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="receptor"):
            Comprobante(1, _solicitud_basica(), 30, None)

    def test_solicitud_none_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="solicitud"):
            Comprobante(1, None, 30, "Juan")

    def test_fecha_hora_none_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="fecha"):
            Comprobante(1, _solicitud_basica(), None, "Juan")

    def test_nro_cero_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="nro"):
            Comprobante(0, _solicitud_basica(), 30, "Juan")

    def test_nro_negativo_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="nro"):
            Comprobante(-1, _solicitud_basica(), 30, "Juan")


class TestConstruccionComprobante:
    def test_guarda_atributos_basicos(self):
        s = _solicitud_basica()
        c = Comprobante(1, s, 30, "Juan")
        assert c.nro == 1
        assert c.solicitud == s
        assert c.fecha_hora_real == 30
        assert c.receptor == "Juan"
