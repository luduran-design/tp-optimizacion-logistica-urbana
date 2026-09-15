"""Tests de MatrizDistancias: agregar tramos, consulta y validaciones."""

import pytest

from modelado import MatrizDistancias, Ubicacion, Deposito, DatosInvalidos, RutaIncompleta


def _matriz_con_ubicaciones():
    """Helper: matriz vacia con 3 ubicaciones (deposito + 2 destinos)."""
    d = Deposito("D1", "Central", "")
    u1 = Ubicacion("U1", "Palermo", "")
    u2 = Ubicacion("U2", "Belgrano", "")
    return MatrizDistancias([d, u1, u2]), d, u1, u2


class TestAgregarTramo:
    def test_agregar_tramo_valido_lo_guarda(self):
        m, d, u1, _ = _matriz_con_ubicaciones()
        m.agregar_tramo(d, u1, 5.0)
        assert m.contiene_tramo(d, u1) is True

    def test_agregar_tramo_negativo_lanza_error(self):
        m, d, u1, _ = _matriz_con_ubicaciones()
        with pytest.raises(DatosInvalidos, match="negativa"):
            m.agregar_tramo(d, u1, -1.0)

    def test_agregar_tramo_cero_es_valido(self):
        # Cero km podria ser un caso borde valido (mismo punto).
        m, d, u1, _ = _matriz_con_ubicaciones()
        m.agregar_tramo(d, u1, 0)
        assert m.contiene_tramo(d, u1) is True


class TestContieneTramo:
    def test_matriz_vacia_no_contiene_nada(self):
        m, d, u1, _ = _matriz_con_ubicaciones()
        assert m.contiene_tramo(d, u1) is False

    def test_contiene_tramo_es_direccional(self):
        # Que exista D -> U1 no implica que exista U1 -> D.
        m, d, u1, _ = _matriz_con_ubicaciones()
        m.agregar_tramo(d, u1, 5.0)
        assert m.contiene_tramo(d, u1) is True
        assert m.contiene_tramo(u1, d) is False


class TestConsultarDistancia:
    def test_distancia_devuelve_el_km_guardado(self):
        m, d, u1, _ = _matriz_con_ubicaciones()
        m.agregar_tramo(d, u1, 5.0)
        assert m.distancia(d, u1) == 5.0

    def test_distancia_de_tramo_inexistente_lanza_ruta_incompleta(self):
        # Regla del dominio: si falta un tramo, no se puede seguir armando el viaje.
        m, d, u1, _ = _matriz_con_ubicaciones()
        with pytest.raises(RutaIncompleta):
            m.distancia(d, u1)

    def test_actualizar_tramo_pisa_el_valor_anterior(self):
        # Si se agrega dos veces el mismo tramo, gana el ultimo.
        m, d, u1, _ = _matriz_con_ubicaciones()
        m.agregar_tramo(d, u1, 5.0)
        m.agregar_tramo(d, u1, 8.0)
        assert m.distancia(d, u1) == 8.0
