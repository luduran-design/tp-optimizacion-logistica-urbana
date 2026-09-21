from modelado.enums import ResultadoParada
from modelado.excepciones import TransicionIlegal


class Parada:
    """Parada de un itinerario: una solicitud a entregar en un orden dado.

    Arranca en estado PENDIENTE. Termina como ENTREGADA (guardando quien recibio
    y cuando) o FALLIDA (guardando el incidente). Una vez fuera de PENDIENTE, no
    se puede volver atras.
    """

    def __init__(self, orden, solicitud, llegada_prevista):
        self.orden = orden
        self.solicitud = solicitud
        self.llegada_prevista = llegada_prevista
        self.resultado = ResultadoParada.PENDIENTE
        # Se completan al cerrar la parada (entregar o marcar_fallida)
        self.receptor = None
        self.fecha_hora_real = None
        self.incidente = None

    def esta_pendiente(self) -> bool:
        return self.resultado == ResultadoParada.PENDIENTE

    def entregar(self, receptor, fecha_hora) -> None:
        """Cierra la parada como ENTREGADA y registra quien recibio y cuando.

        Los datos de entrega quedan guardados en la parada. La validacion del
        receptor (no vacio) la hace el Comprobante, que se fabrica desde Viaje.
        """
        if not self.esta_pendiente():
            raise TransicionIlegal("Solo se puede entregar una parada pendiente")
        self.resultado = ResultadoParada.ENTREGADA
        self.receptor = receptor
        self.fecha_hora_real = fecha_hora

    def marcar_fallida(self, incidente) -> None:
        """Cierra la parada como FALLIDA y guarda el incidente que la motivo."""
        if not self.esta_pendiente():
            raise TransicionIlegal(
                "Solo se puede marcar como fallida una parada pendiente"
            )
        self.resultado = ResultadoParada.FALLIDA
        self.incidente = incidente
