"""Tests de Solicitud: comportamiento y validaciones de constructor."""

import pytest

from modelado import Solicitud, Ubicacion, Ventana, DatosInvalidos
from tests.helpers import _articulos_basicos, _solicitud_basica


class TestSolicitud:
    def test_peso_total_suma_articulos(self):
        s = _solicitud_basica()
        assert s.peso_total() == 7.0

    def test_volumen_total_suma_articulos(self):
        s = _solicitud_basica()
        assert s.volumen_total() == 3.5

    def test_asignacion_arranca_en_false(self):
        assert _solicitud_basica().esta_asignada() is False

    def test_marcar_y_desmarcar_asignada(self):
        s = _solicitud_basica()
        s.marcar_como_asignada()
        assert s.esta_asignada() is True
        s.desmarcar_como_asignada()
        assert s.esta_asignada() is False


class TestValidacionSolicitud:
    def _destino(self):
        return Ubicacion("U1", "Palermo", "")

    def test_id_vacio_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="id"):
            Solicitud("", self._destino(), Ventana(0, 100), _articulos_basicos())

    def test_destino_none_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="destino"):
            Solicitud("S1", None, Ventana(0, 100), _articulos_basicos())

    def test_ventana_none_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="ventana"):
            Solicitud("S1", self._destino(), None, _articulos_basicos())

    def test_articulos_vacio_lanza_error(self):
        # Regla: una solicitud tiene que llevar al menos un articulo.
        with pytest.raises(DatosInvalidos, match="articulo"):
            Solicitud("S1", self._destino(), Ventana(0, 100), [])
