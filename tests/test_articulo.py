"""Tests de validaciones de constructor de Articulo."""

import pytest

from modelado import Articulo, DatosInvalidos


class TestValidacionArticulo:
    def test_id_vacio_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="id"):
            Articulo("", "libro", 1.0, 0.5)

    def test_nombre_vacio_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="nombre"):
            Articulo("A1", "", 1.0, 0.5)

    def test_peso_cero_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="peso"):
            Articulo("A1", "libro", 0, 0.5)

    def test_peso_negativo_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="peso"):
            Articulo("A1", "libro", -1.0, 0.5)

    def test_volumen_cero_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="volumen"):
            Articulo("A1", "libro", 1.0, 0)

    def test_volumen_negativo_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="volumen"):
            Articulo("A1", "libro", 1.0, -0.5)
