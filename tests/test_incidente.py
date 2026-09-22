"""Tests de Incidente (regla 12): tipo, descripcion, instante, afectado e inmutabilidad."""

import pytest

from modelado import Incidente, TipoIncidente, DatosInvalidos
from tests.helpers import _solicitud_basica, _make_transportes


def _incidente_valido(afectado=None):
    if afectado is None:
        afectado = _solicitud_basica()
    return Incidente("I1", TipoIncidente.DANIO, 10, "paquete roto", afectado)


class TestValidacionIncidente:
    def test_incidente_valido_construye(self):
        s = _solicitud_basica()
        i = Incidente("I1", TipoIncidente.DANIO, 10, "paquete roto", s)
        assert i.id == "I1"
        assert i.tipo == TipoIncidente.DANIO
        assert i.fecha_hora == 10
        assert i.descripcion == "paquete roto"
        assert i.afectado is s

    def test_id_vacio_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="id"):
            Incidente("", TipoIncidente.DANIO, 10, "paquete roto", _solicitud_basica())

    def test_tipo_string_libre_lanza_error(self):
        # El ejemplo textual del ayudante: "EL_PERRO_SE_COMIO_EL_PAQUETE"
        # ya no se puede construir.
        with pytest.raises(DatosInvalidos, match="TipoIncidente"):
            Incidente("I1", "EL_PERRO_SE_COMIO_EL_PAQUETE", 10, "x", _solicitud_basica())

    def test_fecha_hora_none_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="fecha"):
            Incidente("I1", TipoIncidente.DANIO, None, "paquete roto", _solicitud_basica())

    def test_descripcion_vacia_lanza_error(self):
        # Regla 12 prohibe descripcion vacia.
        with pytest.raises(DatosInvalidos, match="descripcion"):
            Incidente("I1", TipoIncidente.DANIO, 10, "", _solicitud_basica())

    def test_descripcion_solo_espacios_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="descripcion"):
            Incidente("I1", TipoIncidente.DANIO, 10, "   ", _solicitud_basica())


class TestAfectado:
    """Regla 12: el incidente referencia a una solicitud o a un transporte."""

    def test_afectado_none_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="afectado"):
            Incidente("I1", TipoIncidente.DANIO, 10, "paquete roto", None)

    def test_afectado_de_otro_tipo_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="afectado"):
            Incidente("I1", TipoIncidente.DANIO, 10, "paquete roto", "el chofer")

    def test_afectado_solicitud(self):
        i = _incidente_valido(_solicitud_basica())
        assert i.afecta_a_solicitud() is True
        assert i.afecta_a_transporte() is False

    def test_afectado_transporte(self):
        _, furgoneta, _ = _make_transportes()
        i = _incidente_valido(furgoneta)
        assert i.afecta_a_transporte() is True
        assert i.afecta_a_solicitud() is False


class TestInmutabilidadIncidente:
    """Un incidente es un registro: una vez creado, no se puede reescribir."""

    def test_no_se_puede_reasignar_id(self):
        i = _incidente_valido()
        with pytest.raises(AttributeError):
            i.id = "I99"

    def test_no_se_puede_reasignar_tipo(self):
        i = _incidente_valido()
        with pytest.raises(AttributeError):
            i.tipo = TipoIncidente.AUSENTE

    def test_no_se_puede_reasignar_descripcion(self):
        i = _incidente_valido()
        with pytest.raises(AttributeError):
            i.descripcion = "otra cosa"

    def test_no_se_puede_reasignar_fecha_hora(self):
        i = _incidente_valido()
        with pytest.raises(AttributeError):
            i.fecha_hora = 999

    def test_no_se_puede_reasignar_afectado(self):
        i = _incidente_valido()
        with pytest.raises(AttributeError):
            i.afectado = "otro"