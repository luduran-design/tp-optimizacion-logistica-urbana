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
