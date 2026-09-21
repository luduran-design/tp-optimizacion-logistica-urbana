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


class TestInmutabilidadArticulo:
    """Todos los atributos son de solo lectura desde afuera: no se pueden
    reasignar despues del __init__ (encapsulamiento, checklist)."""

    def test_no_se_puede_reasignar_id(self):
        a = Articulo("A1", "libro", 2.0, 0.5)
        with pytest.raises(AttributeError):
            a.id = "A99"

    def test_no_se_puede_reasignar_peso(self):
        a = Articulo("A1", "libro", 2.0, 0.5)
        with pytest.raises(AttributeError):
            a.peso = -5

    def test_no_se_puede_reasignar_volumen(self):
        a = Articulo("A1", "libro", 2.0, 0.5)
        with pytest.raises(AttributeError):
            a.volumen = 999

    def test_no_se_puede_reasignar_nombre(self):
        a = Articulo("A1", "libro", 2.0, 0.5)
        with pytest.raises(AttributeError):
            a.nombre = "otro"
