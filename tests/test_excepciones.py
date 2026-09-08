"""Tests de la jerarquia de excepciones del dominio."""

import pytest

from modelado import (
    ErrorLogistica,
    DatosInvalidos,
    CapacidadExcedida,
    RutaIncompleta,
    VentanaIncumplida,
    TransicionIlegal,
    Ubicacion,
)


class TestJerarquiaExcepciones:
    # Todas las excepciones del dominio deben heredar de ErrorLogistica.
    # Esto permite atrapar cualquier error del dominio con un solo
    # "except ErrorLogistica" sin tener que listarlas una por una.

    def test_datos_invalidos_hereda_de_error_logistica(self):
        assert issubclass(DatosInvalidos, ErrorLogistica)

    def test_capacidad_excedida_hereda_de_error_logistica(self):
        assert issubclass(CapacidadExcedida, ErrorLogistica)

    def test_ruta_incompleta_hereda_de_error_logistica(self):
        assert issubclass(RutaIncompleta, ErrorLogistica)

    def test_ventana_incumplida_hereda_de_error_logistica(self):
        assert issubclass(VentanaIncumplida, ErrorLogistica)

    def test_transicion_ilegal_hereda_de_error_logistica(self):
        assert issubclass(TransicionIlegal, ErrorLogistica)

    def test_error_logistica_hereda_de_exception(self):
        # Sanity check: la raiz debe ser una Exception normal.
        assert issubclass(ErrorLogistica, Exception)

    def test_datos_invalidos_atrapable_como_error_logistica(self):
        # Uso practico: un solo except cubre toda la familia.
        try:
            Ubicacion("", "nombre", "")
        except ErrorLogistica:
            return  # OK, lo atrapamos
        assert False, "Deberia haberse lanzado un ErrorLogistica"
