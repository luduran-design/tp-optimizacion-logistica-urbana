from abc import ABC, abstractmethod

from modelado.excepciones import DatosInvalidos
from modelado.deposito import Deposito
from modelado.matriz_distancias import MatrizDistancias
from modelado.solicitud import Solicitud


class PoliticaDeOrdenamiento(ABC):
    """Contrato que toda politica cumple para ser intercambiable sin tocar el
    nucleo (regla 13): recibe deposito, solicitudes y matriz, y devuelve una
    lista nueva con el orden sugerido. No modifica ningun viaje ni reserva
    recursos; no garantiza factibilidad de ventanas ni de capacidad."""

    @abstractmethod
    def sugerir_orden(self, deposito, solicitudes, matriz):
        pass

    @staticmethod
    def _validar_entrada(deposito, solicitudes, matriz) -> None:
        if not isinstance(deposito, Deposito):
            raise DatosInvalidos("El deposito debe ser un Deposito.")
        if not isinstance(matriz, MatrizDistancias):
            raise DatosInvalidos("La matriz debe ser una MatrizDistancias.")
        if not isinstance(solicitudes, (list, tuple)):
            raise DatosInvalidos("Las solicitudes deben ser una lista.")
        for s in solicitudes:
            if not isinstance(s, Solicitud):
                raise DatosInvalidos("La lista solo puede contener Solicitud.")


class MenorVentanaPrimero(PoliticaDeOrdenamiento):
    """Prioriza urgencia: ordena por la ventana horaria que cierra antes.
    Ignora la distancia. Es la segunda politica intercambiable exigida por la
    regla 13."""

    def sugerir_orden(self, deposito, solicitudes, matriz):
        self._validar_entrada(deposito, solicitudes, matriz)
        # sorted() devuelve una lista nueva: la lista recibida no se toca.
        return sorted(solicitudes, key=lambda s: s.ventana.fin)


class VecinoMasCercano(PoliticaDeOrdenamiento):
    """Prioriza distancia: empieza por la solicitud mas cercana al deposito y
    sigue, en cada paso, por la mas cercana a la ultima visitada (greedy).
    Ignora las ventanas horarias."""

    def sugerir_orden(self, deposito, solicitudes, matriz):
        self._validar_entrada(deposito, solicitudes, matriz)
        pendientes = list(solicitudes)   # copia: la lista recibida no se toca
        ordenadas = []
        actual = deposito

        while pendientes:
            mas_cercana = min(pendientes, key=lambda s: matriz.distancia(actual, s.destino))
            ordenadas.append(mas_cercana)
            actual = mas_cercana.destino
            pendientes.remove(mas_cercana)

        return ordenadas