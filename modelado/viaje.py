from modelado.enums import EstadoViaje
from modelado.excepciones import TransicionIlegal
from modelado.itinerario import Itinerario


class Viaje:
    def __init__(self, id_viaje, fecha, transporte, deposito, matriz, hora_salida):
        self._id = id_viaje
        self._fecha = fecha
        self._estado = EstadoViaje.PLANIFICADO
        self._itinerario = Itinerario(deposito, hora_salida, matriz, transporte)
        self._comprobantes = []
        self._incidentes = []

    # --- Identidad y estado propios ---
    @property
    def id(self):
        return self._id

    @property
    def fecha(self):
        return self._fecha

    @property
    def estado(self) -> EstadoViaje:
        return self._estado

    @property
    def itinerario(self) -> "Itinerario":
        return self._itinerario

    @property
    def comprobantes(self):
        return list(self._comprobantes)

    @property
    def incidentes(self):
        return list(self._incidentes)

    # --- Delegacion al itinerario ---
    @property
    def paradas(self):
        return self._itinerario.paradas

    def distancia_total(self) -> float:
        return self._itinerario.distancia_total

    def carga_peso(self) -> float:
        return self._itinerario.carga_peso()

    def carga_volumen(self) -> float:
        return self._itinerario.carga_volumen()

    def es_factible(self) -> bool:
        return self._itinerario.es_factible()

    def costo(self) -> float:
        return self._itinerario.costo()

    def impacto_ambiental(self) -> float:
        return self._itinerario.impacto()

    def agregar_solicitud(self, solicitud):
        self._itinerario.agregar(solicitud)

    def quitar_solicitud(self, solicitud):
        pass

    def reordenar(self, secuencia):
        pass

    # --- Maquina de estados (regla 10) ---

    def iniciar(self):
        if self._estado != EstadoViaje.PLANIFICADO:
            raise TransicionIlegal(
                f"No se puede iniciar un viaje en estado {self._estado.value}"
            )
        self._estado = EstadoViaje.EN_CURSO

    def finalizar(self):
        if self._estado != EstadoViaje.EN_CURSO:
            raise TransicionIlegal(
                f"No se puede finalizar un viaje en estado {self._estado.value}"
            )
        self._estado = EstadoViaje.FINALIZADO

    def recorrer(self):
        pass

    def esta_completo(self):
        pass

    def parada_actual(self):
        pass

    def registrar_entrega(self, solicitud, receptor, fecha_hora):
        pass

    def registrar_fallo(self, solicitud, incidente):
        pass

    def registrar_incidente(self, incidente):
        self._incidentes.append(incidente)
