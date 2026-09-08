"""Helpers de construccion reutilizados por varios archivos de test.

Estas funciones construyen objetos "validos por defecto" para que cada test
no tenga que armar todo desde cero. Si necesitas variar algo puntual, pasas
un parametro; si no, tomas el default.

Importalos con:

    from tests.helpers import _articulos_basicos, _solicitud_basica, ...
"""

from modelado import (
    Articulo, Ubicacion, Ventana, Solicitud,
    Motocicleta, Furgoneta, Camion,
    Deposito, MatrizDistancias, Viaje,
)


def _articulos_basicos():
    return [Articulo("A1", "libro", 2.0, 0.5),
            Articulo("A2", "silla", 5.0, 3.0)]


def _solicitud_basica(id="S1"):
    destino = Ubicacion("U1", "Palermo", "")
    return Solicitud(id, destino, Ventana(0, 100), _articulos_basicos())


def _make_transportes(factor=0.27):
    # Mismo factor ambiental para todos: la diferencia SOLO viene
    # de la especializacion de cada subclase.
    m = Motocicleta("M1", 20, 0.5, 40, 100, 50, factor)
    f = Furgoneta("F1", 1000, 5.0, 60, 200, 50, factor)
    c = Camion("C1", 5000, 20.0, 50, 500, 100, factor)
    return m, f, c


def _make_viaje_planificado():
    deposito = Deposito("D1", "Central", "")
    matriz = MatrizDistancias([deposito])
    transporte = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0.27)
    return Viaje("V1", "2026-09-07", transporte, deposito, matriz, 8)
