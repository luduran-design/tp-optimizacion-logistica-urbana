from modelado.enums import ResultadoParada
from modelado.excepciones import TransicionIlegal


class Parada:
    def __init__(self, orden, solicitud, llegada_prevista):
        self.orden = orden
        self.solicitud = solicitud
        self.llegada_prevista = llegada_prevista
        self.resultado = ResultadoParada.PENDIENTE

    def esta_pendiente(self):
        return self.resultado == ResultadoParada.PENDIENTE

    def entregar(self, receptor, fecha_hora):
        if not self.esta_pendiente():
            raise TransicionIlegal("Solo se puede entregar una parada pendiente")
        self.resultado = ResultadoParada.ENTREGADA

    def marcar_fallida(self, incidente):
        if not self.esta_pendiente():
            raise TransicionIlegal("Solo se puede marcar como fallida una parada pendiente")
        self.resultado = ResultadoParada.FALLIDA
