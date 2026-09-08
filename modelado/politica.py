from abc import ABC, abstractmethod


class PoliticaDeOrdenamiento(ABC):
    # Politica abstracta (ABC): define el "contrato" que toda politica debe cumplir para
    # ser intercambiable sin tocar el nucleo (regla 13)

    # Abstracto: cada politica concreta define su propio criterio de orden.
    # Devuelve un orden sugerido, NO modifica ningun viaje (regla 13).
    @abstractmethod
    def sugerir_orden(self, deposito, solicitudes, matriz):
        pass


class VecinoMasCercano(PoliticaDeOrdenamiento):
    # VecinoMasCercano: ordena empezando por la solicitud mas cercana al deposito y
    # siguiendo por la mas cercana a la anterior. Criterio distinto a MenorVentanaPrimero
    # (regla 13 pide 2 politicas que ordenen distinto).
    def sugerir_orden(self, deposito, solicitudes, matriz):
        pass


class MenorVentanaPrimero(PoliticaDeOrdenamiento):
    # MenorVentanaPrimero: ordena por la ventana horaria que cierra antes
    # (las mas urgentes primero). Es la segunda politica intercambiable exigida por la
    # regla 13.
    def sugerir_orden(self, deposito, solicitudes, matriz):
        pass
