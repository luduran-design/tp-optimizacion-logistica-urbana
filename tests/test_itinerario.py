"""Tests de Itinerario: agregar (con atomicidad), quitar, reordenar, factibilidad."""

import pytest

from modelado import (
    Itinerario, MatrizDistancias, Deposito, Ubicacion, Ventana, Solicitud,
    Articulo, Furgoneta, DatosInvalidos, CapacidadExcedida,
)


# ============================================================
# Helpers locales para armar escenarios controlados
# ============================================================

def _escenario_basico():
    """Depósito D + destinos U1 y U2, con una matriz completa (D<->U1<->U2)."""
    d = Deposito("D1", "Central", "")
    u1 = Ubicacion("U1", "Palermo", "")
    u2 = Ubicacion("U2", "Belgrano", "")
    matriz = MatrizDistancias([d, u1, u2])
    # Todos los tramos, en ambas direcciones (necesarios porque la matriz es direccional).
    matriz.agregar_tramo(d, u1, 5.0)
    matriz.agregar_tramo(u1, d, 5.0)
    matriz.agregar_tramo(d, u2, 8.0)
    matriz.agregar_tramo(u2, d, 8.0)
    matriz.agregar_tramo(u1, u2, 3.0)
    matriz.agregar_tramo(u2, u1, 3.0)
    return d, u1, u2, matriz


def _solicitud_liviana(id, destino, peso=1.0):
    """Solicitud con un articulo liviano, cabe en cualquier transporte razonable."""
    art = Articulo(f"A-{id}", "paquete", peso, 0.1)
    return Solicitud(id, destino, Ventana(0, 100), [art])


def _itinerario_con_furgoneta_grande(deposito, matriz):
    """Furgoneta con mucha capacidad: los tests que no la excedan no la excederan."""
    f = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0.27)
    return Itinerario(deposito, hora_salida=8, matriz=matriz, transporte=f)


def _itinerario_con_furgoneta_chica(deposito, matriz):
    """Furgoneta con capacidad de solo 10 kg: sirve para forzar CapacidadExcedida."""
    f = Furgoneta("F1", 10, 5.0, 60, 200, 50, 0.27)
    return Itinerario(deposito, hora_salida=8, matriz=matriz, transporte=f)


# ============================================================
# Estado inicial
# ============================================================

class TestItinerarioVacio:
    def test_paradas_arrancan_vacias(self):
        d, _, _, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        assert it.paradas == []

    def test_distancia_arranca_en_cero(self):
        d, _, _, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        assert it.distancia_total == 0.0

    def test_carga_arranca_en_cero(self):
        d, _, _, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        assert it.carga_peso() == 0
        assert it.carga_volumen() == 0


# ============================================================
# Agregar (con revalidacion atomica -- regla 7)
# ============================================================

class TestAgregarSolicitud:
    def test_agregar_solicitud_factible_agrega_parada(self):
        d, u1, _, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        s = _solicitud_liviana("S1", u1, peso=2.0)
        it.agregar(s)
        assert len(it.paradas) == 1

    def test_agregar_recalcula_distancia_total(self):
        # Con una sola parada: D -> U1 -> D = 5 + 5 = 10
        d, u1, _, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        it.agregar(_solicitud_liviana("S1", u1, peso=2.0))
        assert it.distancia_total == 10.0

    def test_agregar_marca_la_solicitud_como_asignada(self):
        d, u1, _, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        s = _solicitud_liviana("S1", u1, peso=2.0)
        it.agregar(s)
        assert s.esta_asignada() is True

    def test_agregar_solicitud_que_excede_capacidad_lanza_error(self):
        # Furgoneta de 10 kg + solicitud de 50 kg = no factible.
        d, u1, _, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_chica(d, matriz)
        s_pesada = _solicitud_liviana("S1", u1, peso=50.0)
        with pytest.raises(CapacidadExcedida):
            it.agregar(s_pesada)

    def test_atomicidad_estado_no_cambia_si_falla(self):
        """Regla 7: si agregar deja el itinerario no factible, se revierte todo."""
        d, u1, u2, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_chica(d, matriz)
        # Agregar una liviana que si entra
        s_ok = _solicitud_liviana("S1", u1, peso=5.0)
        it.agregar(s_ok)
        paradas_previas = it.paradas
        distancia_previa = it.distancia_total

        # Ahora intentar agregar una que rompe la capacidad
        # (destino distinto para que la ruta sea calculable)
        s_pesada = _solicitud_liviana("S2", u2, peso=50.0)
        with pytest.raises(CapacidadExcedida):
            it.agregar(s_pesada)

        # El itinerario tiene que estar IDENTICO a como estaba antes del intento
        assert it.paradas == paradas_previas
        assert it.distancia_total == distancia_previa
        assert s_pesada.esta_asignada() is False


# ============================================================
# Quitar
# ============================================================

class TestQuitarSolicitud:
    def test_quitar_saca_la_parada(self):
        d, u1, _, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        s = _solicitud_liviana("S1", u1, peso=2.0)
        it.agregar(s)
        it.quitar(s)
        assert it.paradas == []

    def test_quitar_recalcula_distancia(self):
        d, u1, _, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        s = _solicitud_liviana("S1", u1, peso=2.0)
        it.agregar(s)
        it.quitar(s)
        assert it.distancia_total == 0.0

    def test_quitar_desmarca_la_solicitud(self):
        d, u1, _, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        s = _solicitud_liviana("S1", u1, peso=2.0)
        it.agregar(s)
        it.quitar(s)
        assert s.esta_asignada() is False

    def test_quitar_solicitud_inexistente_lanza_error(self):
        d, u1, _, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        s_no_asignada = _solicitud_liviana("S99", u1, peso=2.0)
        with pytest.raises(DatosInvalidos):
            it.quitar(s_no_asignada)


# ============================================================
# Reordenar
# ============================================================

class TestReordenar:
    def test_reordenar_con_las_mismas_solicitudes_cambia_orden(self):
        d, u1, u2, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        s1 = _solicitud_liviana("S1", u1, peso=2.0)
        s2 = _solicitud_liviana("S2", u2, peso=2.0)
        it.agregar(s1)
        it.agregar(s2)
        # Reordeno para que S2 vaya primero
        it.reordenar([s2, s1])
        assert [p.solicitud for p in it.paradas] == [s2, s1]

    def test_reordenar_renumera_las_paradas(self):
        d, u1, u2, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        s1 = _solicitud_liviana("S1", u1, peso=2.0)
        s2 = _solicitud_liviana("S2", u2, peso=2.0)
        it.agregar(s1)
        it.agregar(s2)
        it.reordenar([s2, s1])
        assert it.paradas[0].orden == 1
        assert it.paradas[1].orden == 2

    def test_reordenar_con_secuencia_distinta_lanza_error(self):
        # No se puede reordenar agregando o quitando: solo permutar las mismas solicitudes.
        d, u1, u2, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        s1 = _solicitud_liviana("S1", u1, peso=2.0)
        s2 = _solicitud_liviana("S2", u2, peso=2.0)
        s_ajena = _solicitud_liviana("S99", u1, peso=2.0)
        it.agregar(s1)
        it.agregar(s2)
        with pytest.raises(DatosInvalidos):
            it.reordenar([s1, s_ajena])  # s_ajena no esta en el itinerario


# ============================================================
# Factibilidad
# ============================================================

class TestFactibilidad:
    def test_itinerario_vacio_es_factible(self):
        d, _, _, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        assert it.es_factible() is True

    def test_itinerario_con_carga_dentro_de_capacidad_es_factible(self):
        d, u1, _, matriz = _escenario_basico()
        it = _itinerario_con_furgoneta_grande(d, matriz)
        it.agregar(_solicitud_liviana("S1", u1, peso=2.0))
        assert it.es_factible() is True
