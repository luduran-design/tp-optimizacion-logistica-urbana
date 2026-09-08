"""Tests de Deposito (subtipo de Ubicacion)."""

from modelado import Deposito, Ubicacion


class TestDeposito:
    def test_es_deposito_true(self):
        assert Deposito("D1", "Central", "").es_deposito() is True

    def test_deposito_es_una_ubicacion(self):
        # Herencia: un Deposito debe ser una Ubicacion.
        assert isinstance(Deposito("D1", "Central", ""), Ubicacion)
