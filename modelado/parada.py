from modelado.enums import ResultadoParada
from modelado.excepciones import TransicionIlegal


class Parada:
    """Parada de un itinerario: una solicitud a entregar en un orden dado.

    El estado (resultado, receptor, fecha_hora_real, incidente) es privado y solo
    se puede modificar a traves de entregar() o marcar_fallida(). El orden dentro
    del itinerario se cambia con actualizar_orden(), llamado por Itinerario cuando
    reordena o quita paradas.
    """

    def __init__(self, orden, solicitud, llegada_prevista):
        self._orden = orden
        self._solicitud = solicitud
        self._llegada_prevista = llegada_prevista
        self._resultado = ResultadoParada.PENDIENTE
        # Se completan al cerrar la parada (entregar o marcar_fallida)
        self._receptor = None
        self._fecha_hora_real = None
        self._incidente = None

    @property
    def orden(self):
        return self._orden

    @property
    def solicitud(self):
        return self._solicitud

    @property
    def llegada_prevista(self):
        return self._llegada_prevista

    @property
    def resultado(self) -> ResultadoParada:
        return self._resultado

    @property
    def receptor(self):
        return self._receptor

    @property
    def fecha_hora_real(self):
        return self._fecha_hora_real

    @property
    def incidente(self):
        return self._incidente

    def actualizar_orden(self, nuevo_orden) -> None:
        """Reasigna la posicion de la parada dentro del itinerario.

        Es la unica via legitima para cambiar el orden desde afuera. Solo tiene
        sentido llamarla desde Itinerario cuando reordena o quita paradas.
        """
        self._orden = nuevo_orden

    def esta_pendiente(self) -> bool:
        return self._resultado == ResultadoParada.PENDIENTE

    def entregar(self, receptor, fecha_hora) -> None:
        """Cierra la parada como ENTREGADA y registra quien recibio y cuando.

        Los datos de entrega quedan guardados en la parada. La validacion del
        receptor (no vacio) la hace el Comprobante, que se fabrica desde Viaje.
        """
        if not self.esta_pendiente():
            raise TransicionIlegal("Solo se puede entregar una parada pendiente")
        self._resultado = ResultadoParada.ENTREGADA
        self._receptor = receptor
        self._fecha_hora_real = fecha_hora

    def marcar_fallida(self, incidente) -> None:
        """Cierra la parada como FALLIDA y guarda el incidente que la motivo."""
        if not self.esta_pendiente():
            raise TransicionIlegal(
                "Solo se puede marcar como fallida una parada pendiente"
            )
        self._resultado = ResultadoParada.FALLIDA
        self._incidente = incidente
