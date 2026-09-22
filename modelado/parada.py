from datetime import datetime

from modelado.enums import ResultadoParada
from modelado.excepciones import TransicionIlegal, DatosInvalidos
from modelado.solicitud import Solicitud


class Parada:
    """Parada de un itinerario: una solicitud a entregar en un orden dado.

    El estado (resultado, receptor, fecha_hora_real, incidente) es privado y solo
    se puede modificar a traves de entregar() o marcar_fallida(). El orden y la
    llegada prevista los recalcula Itinerario con actualizar_orden() y
    actualizar_llegada() cada vez que agrega, quita o reordena paradas.

    Convencion de tiempos: la llegada prevista y la fecha/hora real son datetime.
    """

    def __init__(self, orden, solicitud, llegada_prevista):
        self._validar_orden(orden)
        if not isinstance(solicitud, Solicitud):
            raise DatosInvalidos("La solicitud de la parada debe ser una Solicitud.")
        self._validar_llegada(llegada_prevista)
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

    # --- Validaciones ---

    @staticmethod
    def _validar_orden(orden) -> None:
        if isinstance(orden, bool) or not isinstance(orden, int) or orden < 1:
            raise DatosInvalidos(
                "El orden de la parada debe ser un entero mayor o igual a 1."
            )

    @staticmethod
    def _validar_llegada(llegada) -> None:
        if not isinstance(llegada, datetime):
            raise DatosInvalidos("La llegada prevista debe ser un datetime.")

    # --- Recalculo (solo lo usa Itinerario) ---

    def actualizar_orden(self, nuevo_orden) -> None:
        """Reasigna la posicion de la parada dentro del itinerario.

        Es la unica via legitima para cambiar el orden desde afuera. Solo tiene
        sentido llamarla desde Itinerario cuando reordena o quita paradas.
        """
        self._validar_orden(nuevo_orden)
        self._orden = nuevo_orden

    def actualizar_llegada(self, nueva_llegada) -> None:
        """Reasigna la llegada prevista. Solo la usa Itinerario al recalcular."""
        self._validar_llegada(nueva_llegada)
        self._llegada_prevista = nueva_llegada

    # --- Maquina de estados (regla 11) ---

    def esta_pendiente(self) -> bool:
        return self._resultado == ResultadoParada.PENDIENTE

    def entregar(self, receptor, fecha_hora) -> None:
        """Cierra la parada como ENTREGADA y registra quien recibio y cuando.

        Regla 11: receptor no vacio y fecha/hora real. Viaje fabrica el
        Comprobante antes de llamar aca, asi que esta validacion es la red de
        seguridad para quien use Parada directamente.
        """
        if not self.esta_pendiente():
            raise TransicionIlegal("Solo se puede entregar una parada pendiente")
        if not isinstance(receptor, str) or not receptor.strip():
            raise DatosInvalidos("El receptor de la entrega no puede estar vacio")
        if not isinstance(fecha_hora, datetime):
            raise DatosInvalidos("La fecha y hora de la entrega debe ser un datetime")
        self._resultado = ResultadoParada.ENTREGADA
        self._receptor = receptor
        self._fecha_hora_real = fecha_hora

    def marcar_fallida(self, incidente) -> None:
        """Cierra la parada como FALLIDA y guarda el incidente que la motivo.
        Que el incidente sea valido y del viaje lo garantiza Viaje (regla 11)."""
        if not self.esta_pendiente():
            raise TransicionIlegal(
                "Solo se puede marcar como fallida una parada pendiente"
            )
        self._resultado = ResultadoParada.FALLIDA
        self._incidente = incidente

    def __repr__(self):
        return f"Parada({self._orden}, {self._solicitud!r}, {self._resultado.name})"