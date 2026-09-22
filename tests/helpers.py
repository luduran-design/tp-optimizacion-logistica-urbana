"""Helpers de construccion reutilizados por varios archivos de test.

Estas funciones construyen objetos "validos por defecto" para que cada test
no tenga que armar todo desde cero. Si necesitas variar algo puntual, pasas
un parametro; si no, tomas el default.

Convencion de tiempos (regla 6 y requisito de datetime): todo ocurre el mismo
dia, FECHA, y los instantes son datetime completos. Las ventanas se arman con
_ventana(h_ini, h_fin) y un instante con _hora(h, m).

Importalos con:

    from tests.helpers import _hora, _ventana, _solicitud_basica, ...
"""

from datetime import date, datetime

from modelado import (
    Articulo, Ubicacion, Ventana, Solicitud,
    Motocicleta, Furgoneta, Camion,
    Deposito, MatrizDistancias, Viaje,
)

FECHA = date(2026, 9, 22)


def _hora(h, m=0):
    """datetime de la fecha de prueba a las h:m."""
    return datetime(FECHA.year, FECHA.month, FECHA.day, h, m)


def _ventana(h_ini, h_fin, m_ini=0, m_fin=0):
    """Ventana [h_ini:m_ini, h_fin:m_fin] de la fecha de prueba."""
    return Ventana(_hora(h_ini, m_ini), _hora(h_fin, m_fin))


def _ventana_amplia():
    """Cubre todo el dia: para tests que no miran horarios."""
    return _ventana(0, 23, 0, 59)


def _articulos_basicos():
    return [Articulo("A1", "libro", 2.0, 0.5),
            Articulo("A2", "silla", 5.0, 3.0)]


def _solicitud_basica(id="S1"):
    destino = Ubicacion("U1", "Palermo", "")
    return Solicitud(id, destino, _ventana_amplia(), _articulos_basicos())


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
    return Viaje("V1", FECHA, transporte, deposito, matriz, _hora(8))