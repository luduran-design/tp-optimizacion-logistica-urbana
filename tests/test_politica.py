"""Tests de las politicas de ordenamiento.

Estos tests validan el comportamiento que PROMETE cada nombre de politica:
- VecinoMasCercano: ordena por distancia, arranca por la mas cercana al deposito
  y sigue por la mas cercana a la anterior (algoritmo greedy).
- MenorVentanaPrimero: ordena por ventana horaria, la que cierra antes va primero.

Si estos tests fallan, es porque las implementaciones en politica.py no coinciden
con los nombres. Ver nota al final del mensaje del ayudante."""

import pytest

from modelado import (
    VecinoMasCercano, MenorVentanaPrimero,
    Deposito, Ubicacion, Ventana, Solicitud, Articulo, MatrizDistancias,
    DatosInvalidos,
)
from tests.helpers import _hora


# ============================================================
# Helpers
# ============================================================

def _art():
    return [Articulo("A1", "paquete", 1.0, 0.1)]


def _solicitud(id, destino, ventana_fin):
    """Solicitud con ventana desde las 00:00 hasta la hora `ventana_fin` (entera)."""
    return Solicitud(id, destino, Ventana(_hora(0), _hora(ventana_fin)), _art())


def _escenario():
    """Deposito D y tres destinos U1, U2, U3 con distancias asimetricas."""
    d = Deposito("D1", "Central", "")
    u1 = Ubicacion("U1", "Palermo", "")
    u2 = Ubicacion("U2", "Belgrano", "")
    u3 = Ubicacion("U3", "Caballito", "")
    matriz = MatrizDistancias([d, u1, u2, u3])
    # Distancias desde el deposito (U3 es la mas cercana)
    matriz.agregar_tramo(d, u1, 10)
    matriz.agregar_tramo(d, u2, 20)
    matriz.agregar_tramo(d, u3, 5)
    # Distancias entre destinos (para que el greedy tenga que elegir)
    matriz.agregar_tramo(u3, u1, 3)   # de U3, lo mas cercano es U1
    matriz.agregar_tramo(u3, u2, 15)
    matriz.agregar_tramo(u1, u2, 4)   # de U1, lo mas cercano es U2
    matriz.agregar_tramo(u1, u3, 3)
    matriz.agregar_tramo(u2, u1, 4)
    matriz.agregar_tramo(u2, u3, 15)
    return d, u1, u2, u3, matriz


# ============================================================
# VecinoMasCercano
# ============================================================

class TestVecinoMasCercano:
    def test_arranca_por_la_mas_cercana_al_deposito(self):
        d, u1, u2, u3, matriz = _escenario()
        # Ventanas iguales para que la politica solo mire distancias.
        s1 = _solicitud("S1", u1, 18)
        s2 = _solicitud("S2", u2, 18)
        s3 = _solicitud("S3", u3, 18)
        politica = VecinoMasCercano()
        orden = politica.sugerir_orden(d, [s1, s2, s3], matriz)
        # U3 esta a 5 km (la mas cercana al deposito), tiene que ir primera.
        assert orden[0] == s3

    def test_sigue_por_la_mas_cercana_a_la_anterior(self):
        d, u1, u2, u3, matriz = _escenario()
        s1 = _solicitud("S1", u1, 18)
        s2 = _solicitud("S2", u2, 18)
        s3 = _solicitud("S3", u3, 18)
        politica = VecinoMasCercano()
        orden = politica.sugerir_orden(d, [s1, s2, s3], matriz)
        # Empezando en U3: lo mas cercano es U1 (3 km).
        # Despues desde U1 solo queda U2 (4 km).
        assert orden == [s3, s1, s2]

    def test_devuelve_todas_las_solicitudes(self):
        d, u1, u2, u3, matriz = _escenario()
        s1 = _solicitud("S1", u1, 18)
        s2 = _solicitud("S2", u2, 18)
        s3 = _solicitud("S3", u3, 18)
        politica = VecinoMasCercano()
        orden = politica.sugerir_orden(d, [s1, s2, s3], matriz)
        assert set(orden) == {s1, s2, s3}


# ============================================================
# MenorVentanaPrimero
# ============================================================

class TestMenorVentanaPrimero:
    def test_ordena_por_ventana_fin_ascendente(self):
        d, u1, u2, u3, matriz = _escenario()
        # Ventanas distintas: S2 cierra primero, S1 despues, S3 al final.
        s1 = _solicitud("S1", u1, ventana_fin=12)
        s2 = _solicitud("S2", u2, ventana_fin=9)
        s3 = _solicitud("S3", u3, ventana_fin=15)
        politica = MenorVentanaPrimero()
        orden = politica.sugerir_orden(d, [s1, s2, s3], matriz)
        assert orden == [s2, s1, s3]

    def test_no_depende_de_distancias(self):
        # Aunque U3 esta cerca del deposito, si su ventana cierra tarde va al final.
        d, _, u2, u3, matriz = _escenario()
        s_urgente_lejos = _solicitud("S1", u2, ventana_fin=8)   # lejos pero urgente
        s_tranqui_cerca = _solicitud("S2", u3, ventana_fin=18)  # cerca pero tranqui
        politica = MenorVentanaPrimero()
        orden = politica.sugerir_orden(d, [s_tranqui_cerca, s_urgente_lejos], matriz)
        assert orden == [s_urgente_lejos, s_tranqui_cerca]

    def test_devuelve_todas_las_solicitudes(self):
        d, u1, u2, u3, matriz = _escenario()
        s1 = _solicitud("S1", u1, 12)
        s2 = _solicitud("S2", u2, 9)
        s3 = _solicitud("S3", u3, 15)
        politica = MenorVentanaPrimero()
        orden = politica.sugerir_orden(d, [s1, s2, s3], matriz)
        assert set(orden) == {s1, s2, s3}


# ============================================================
# Las dos politicas son intercambiables (regla 13)
# ============================================================

class TestPoliticasIntercambiables:
    def test_ambas_devuelven_una_lista_del_mismo_tamano(self):
        # Regla 13: son intercambiables. Cualquier codigo cliente puede llamar
        # a cualquiera sin cambiar el tipo de resultado.
        d, u1, u2, u3, matriz = _escenario()
        s1 = _solicitud("S1", u1, 12)
        s2 = _solicitud("S2", u2, 9)
        s3 = _solicitud("S3", u3, 15)

        for politica in (VecinoMasCercano(), MenorVentanaPrimero()):
            orden = politica.sugerir_orden(d, [s1, s2, s3], matriz)
            assert len(orden) == 3


# ============================================================
# Regla 13: consultivas. No modifican la lista ni asignan solicitudes.
# ============================================================

class TestPoliticasSinEfectos:
    def test_no_modifican_la_lista_recibida_ni_asignan(self):
        d, u1, u2, u3, matriz = _escenario()
        s1 = _solicitud("S1", u1, 12)
        s2 = _solicitud("S2", u2, 9)
        s3 = _solicitud("S3", u3, 15)
        original = [s1, s2, s3]
        for politica in (VecinoMasCercano(), MenorVentanaPrimero()):
            orden = politica.sugerir_orden(d, original, matriz)
            assert orden is not original
            assert original == [s1, s2, s3]
            assert all(not s.esta_asignada() for s in original)

    def test_las_dos_politicas_ordenan_distinto_la_misma_lista(self):
        # Prueba minima del enunciado: dos politicas, misma lista, resultados distintos.
        d, u1, u2, u3, matriz = _escenario()
        s1 = _solicitud("S1", u1, 12)
        s2 = _solicitud("S2", u2, 9)
        s3 = _solicitud("S3", u3, 15)
        por_distancia = VecinoMasCercano().sugerir_orden(d, [s1, s2, s3], matriz)
        por_urgencia = MenorVentanaPrimero().sugerir_orden(d, [s1, s2, s3], matriz)
        assert por_distancia == [s3, s1, s2]
        assert por_urgencia == [s2, s1, s3]
        assert por_distancia != por_urgencia

    def test_entrada_invalida_lanza_error(self):
        d, u1, _, _, matriz = _escenario()
        s1 = _solicitud("S1", u1, 12)
        with pytest.raises(DatosInvalidos):
            VecinoMasCercano().sugerir_orden(u1, [s1], matriz)      # u1 no es un Deposito
        with pytest.raises(DatosInvalidos):
            MenorVentanaPrimero().sugerir_orden(d, [s1, "S2"], matriz)