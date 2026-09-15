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
)


# ============================================================
# Helpers
# ============================================================

def _art():
    return [Articulo("A1", "paquete", 1.0, 0.1)]


def _solicitud(id, destino, ventana_fin):
    """Solicitud con ventana que va de 0 a `ventana_fin`."""
    return Solicitud(id, destino, Ventana(0, ventana_fin), _art())


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
        s1 = _solicitud("S1", u1, 100)
        s2 = _solicitud("S2", u2, 100)
        s3 = _solicitud("S3", u3, 100)
        politica = VecinoMasCercano()
        orden = politica.sugerir_orden(d, [s1, s2, s3], matriz)
        # U3 esta a 5 km (la mas cercana al deposito), tiene que ir primera.
        assert orden[0] == s3

    def test_sigue_por_la_mas_cercana_a_la_anterior(self):
        d, u1, u2, u3, matriz = _escenario()
        s1 = _solicitud("S1", u1, 100)
        s2 = _solicitud("S2", u2, 100)
        s3 = _solicitud("S3", u3, 100)
        politica = VecinoMasCercano()
        orden = politica.sugerir_orden(d, [s1, s2, s3], matriz)
        # Empezando en U3: lo mas cercano es U1 (3 km).
        # Despues desde U1 solo queda U2 (4 km).
        assert orden == [s3, s1, s2]

    def test_devuelve_todas_las_solicitudes(self):
        d, u1, u2, u3, matriz = _escenario()
        s1 = _solicitud("S1", u1, 100)
        s2 = _solicitud("S2", u2, 100)
        s3 = _solicitud("S3", u3, 100)
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
        s1 = _solicitud("S1", u1, ventana_fin=50)
        s2 = _solicitud("S2", u2, ventana_fin=20)
        s3 = _solicitud("S3", u3, ventana_fin=90)
        politica = MenorVentanaPrimero()
        orden = politica.sugerir_orden(d, [s1, s2, s3], matriz)
        assert orden == [s2, s1, s3]

    def test_no_depende_de_distancias(self):
        # Aunque U3 esta cerca del deposito, si su ventana cierra tarde va al final.
        d, _, u2, u3, matriz = _escenario()
        s_urgente_lejos = _solicitud("S1", u2, ventana_fin=10)   # lejos pero urgente
        s_tranqui_cerca = _solicitud("S2", u3, ventana_fin=100)  # cerca pero tranqui
        politica = MenorVentanaPrimero()
        orden = politica.sugerir_orden(d, [s_tranqui_cerca, s_urgente_lejos], matriz)
        assert orden == [s_urgente_lejos, s_tranqui_cerca]

    def test_devuelve_todas_las_solicitudes(self):
        d, u1, u2, u3, matriz = _escenario()
        s1 = _solicitud("S1", u1, 50)
        s2 = _solicitud("S2", u2, 20)
        s3 = _solicitud("S3", u3, 90)
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
        s1 = _solicitud("S1", u1, 50)
        s2 = _solicitud("S2", u2, 20)
        s3 = _solicitud("S3", u3, 90)

        for politica in (VecinoMasCercano(), MenorVentanaPrimero()):
            orden = politica.sugerir_orden(d, [s1, s2, s3], matriz)
            assert len(orden) == 3
