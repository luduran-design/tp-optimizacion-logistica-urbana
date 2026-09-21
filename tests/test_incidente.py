"""Tests de validacion de Incidente (enum TipoIncidente + descripcion)."""

import pytest

from modelado import Incidente, TipoIncidente, DatosInvalidos


class TestEnumIncidente:
    def test_tipo_valido_construye(self):
        i = Incidente("I1", TipoIncidente.DANIO, 10, "paquete roto", None)
        assert i.tipo == TipoIncidente.DANIO

    def test_tipo_string_libre_lanza_error(self):
        # El ejemplo textual del ayudante: "EL_PERRO_SE_COMIO_EL_PAQUETE"
        # ya no se puede construir.
        with pytest.raises(DatosInvalidos, match="TipoIncidente"):
            Incidente("I1", "EL_PERRO_SE_COMIO_EL_PAQUETE", 10, "x", None)

    def test_descripcion_vacia_lanza_error(self):
        # Regla 12 prohibe descripcion vacia.
        with pytest.raises(DatosInvalidos, match="descripcion"):
            Incidente("I1", TipoIncidente.DANIO, 10, "", None)


class TestInmutabilidadIncidente:
    """Un incidente es un registro: una vez creado, no se puede reescribir."""

    def _incidente(self):
        return Incidente("I1", TipoIncidente.DANIO, 10, "paquete roto", None)

    def test_no_se_puede_reasignar_id(self):
        i = self._incidente()
        with pytest.raises(AttributeError):
            i.id = "I99"

    def test_no_se_puede_reasignar_tipo(self):
        i = self._incidente()
        with pytest.raises(AttributeError):
            i.tipo = TipoIncidente.AUSENTE

    def test_no_se_puede_reasignar_descripcion(self):
        i = self._incidente()
        with pytest.raises(AttributeError):
            i.descripcion = "otra cosa"

    def test_no_se_puede_reasignar_fecha_hora(self):
        i = self._incidente()
        with pytest.raises(AttributeError):
            i.fecha_hora = 999

    def test_no_se_puede_reasignar_afectado(self):
        i = self._incidente()
        with pytest.raises(AttributeError):
            i.afectado = "otro"
