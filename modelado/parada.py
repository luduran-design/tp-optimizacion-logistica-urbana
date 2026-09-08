from modelado.excepciones import DatosInvalidos
from modelado.enums import ResultadoParada


class Parada:
    def __init__(self, orden, solicitud, llegada_prevista, resultado):
        if not isinstance(resultado, ResultadoParada):
            raise DatosInvalidos(f"resultado debe ser un ResultadoParada, no {resultado!r}")
        self.orden = orden
        self.solicitud = solicitud
        self.llegada_prevista = llegada_prevista
        self.resultado = resultado

    def esta_pendiente(self):
        pass

    def entregar(self, receptor, fecha_hora):
        pass

    def marcar_fallida(self, incidente):
        pass
