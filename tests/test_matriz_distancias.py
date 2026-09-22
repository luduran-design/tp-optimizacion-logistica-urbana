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
class TestUbicacionesConocidas:
    """La matriz conoce sus ubicaciones (regla 1: ids unicos; regla 3: tramos solo
    entre ubicaciones conocidas)."""

    def test_ubicaciones_duplicadas_lanzan_error(self):
        d = Deposito("D1", "Central", "")
        repetida = Ubicacion("D1", "Otra con el mismo id", "")
        with pytest.raises(DatosInvalidos, match="duplicada"):
            MatrizDistancias([d, repetida])

    def test_ubicaciones_devuelve_las_cargadas(self):
        m, d, u1, u2 = _matriz_con_ubicaciones()
        assert m.ubicaciones == [d, u1, u2]

    def test_ubicaciones_devuelve_copia_defensiva(self):
        m, d, u1, u2 = _matriz_con_ubicaciones()
        m.ubicaciones.clear()
        assert m.ubicaciones == [d, u1, u2]

    def test_contiene_ubicacion(self):
        m, d, _, _ = _matriz_con_ubicaciones()
        assert m.contiene_ubicacion(d) is True
        assert m.contiene_ubicacion(Ubicacion("U99", "Desconocida", "")) is False

    def test_agregar_tramo_con_ubicacion_desconocida_lanza_error(self):
        m, d, _, _ = _matriz_con_ubicaciones()
        desconocida = Ubicacion("U99", "Desconocida", "")
        with pytest.raises(DatosInvalidos, match="no pertenece"):
            m.agregar_tramo(d, desconocida, 5.0)
        with pytest.raises(DatosInvalidos, match="no pertenece"):
            m.agregar_tramo(desconocida, d, 5.0)


class TestDistanciaASiMisma:
    """Regla 3: la distancia entre una ubicacion y si misma es cero."""

    def test_distancia_a_si_misma_es_cero_sin_cargarla(self):
        m, d, u1, _ = _matriz_con_ubicaciones()
        assert m.distancia(d, d) == 0.0
        assert m.distancia(u1, u1) == 0.0

    def test_contiene_tramo_a_si_misma_es_true(self):
        m, d, _, _ = _matriz_con_ubicaciones()
        assert m.contiene_tramo(d, d) is True

    def test_cargar_tramo_a_si_misma_distinto_de_cero_lanza_error(self):
        m, d, _, _ = _matriz_con_ubicaciones()
        with pytest.raises(DatosInvalidos, match="si misma"):
            m.agregar_tramo(d, d, 5.0)

    def test_cargar_tramo_a_si_misma_en_cero_es_valido(self):
        m, d, _, _ = _matriz_con_ubicaciones()
        m.agregar_tramo(d, d, 0)
        assert m.distancia(d, d) == 0.0


class TestMatrizDirigida:
    """Regla 3: los tramos se definen en el sentido recorrido."""

    def test_distancia_en_sentido_contrario_lanza_ruta_incompleta(self):
        m, d, u1, _ = _matriz_con_ubicaciones()
        m.agregar_tramo(d, u1, 5.0)
        assert m.distancia(d, u1) == 5.0
        with pytest.raises(RutaIncompleta):
            m.distancia(u1, d)

    def test_ida_y_vuelta_pueden_tener_distancias_distintas(self):
        m, d, u1, _ = _matriz_con_ubicaciones()
        m.agregar_tramo(d, u1, 5.0)
        m.agregar_tramo(u1, d, 7.0)
        assert m.distancia(d, u1) == 5.0
        assert m.distancia(u1, d) == 7.0