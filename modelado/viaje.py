from modelado.enums import EstadoViaje
from modelado.excepciones import TransicionIlegal, DatosInvalidos
from modelado.itinerario import Itinerario
from modelado.comprobante import Comprobante


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

    # --- Guardia de estado compartida (reglas 10 y 12) ---
    def _exigir_planificado(self, accion: str) -> None:
        if self._estado != EstadoViaje.PLANIFICADO:
            raise TransicionIlegal(
                f"No se puede {accion} un viaje en estado {self._estado.value}"
            )

    def agregar_solicitud(self, solicitud):
        self._exigir_planificado("agregar solicitudes a")
        self._itinerario.agregar(solicitud)

    def quitar_solicitud(self, solicitud):
        self._exigir_planificado("quitar solicitudes de")
        self._itinerario.quitar(solicitud)

    def reordenar(self, secuencia):
        self._exigir_planificado("reordenar")
        self._itinerario.reordenar(secuencia)

    # --- Maquina de estados (regla 10) ---

    def iniciar(self):
        self._exigir_planificado("iniciar")
        if not self._itinerario.paradas:
            raise TransicionIlegal("No se puede iniciar un viaje sin paradas")
        if not self.es_factible():
            raise TransicionIlegal(
                "No se puede iniciar un viaje con itinerario no factible"
            )
        self._estado = EstadoViaje.EN_CURSO

    def finalizar(self):
        if self._estado != EstadoViaje.EN_CURSO:
            raise TransicionIlegal(
                f"No se puede finalizar un viaje en estado {self._estado.value}"
            )
        if not self.esta_completo():
            raise TransicionIlegal(
                "No se puede finalizar: hay paradas sin resultado"
            )
        self._estado = EstadoViaje.FINALIZADO

    def recorrer(self):
        if self._estado == EstadoViaje.PLANIFICADO:
            self.iniciar()
        elif self._estado == EstadoViaje.EN_CURSO and self.esta_completo():
            self.finalizar()

    def esta_completo(self):
        return all(not p.esta_pendiente() for p in self._itinerario.paradas)

    def parada_actual(self):
        return next((p for p in self._itinerario.paradas if p.esta_pendiente()), None)

    def registrar_entrega(self, solicitud, receptor, fecha_hora):
        if self._estado != EstadoViaje.EN_CURSO:
            raise TransicionIlegal("Solo se pueden registrar entregas en estado EN_CURSO")
        parada = next((p for p in self._itinerario.paradas if p.solicitud == solicitud), None)
        if parada is None:
            raise DatosInvalidos(f"La solicitud {solicitud.id} no esta en este viaje")
        parada.entregar(receptor, fecha_hora)
        comprobante = Comprobante(len(self._comprobantes) + 1, solicitud, fecha_hora, receptor)
        self._comprobantes.append(comprobante)

    def registrar_fallo(self, solicitud, incidente):
        if self._estado != EstadoViaje.EN_CURSO:
            raise TransicionIlegal("Solo se pueden registrar fallos en estado EN_CURSO")
        parada = next((p for p in self._itinerario.paradas if p.solicitud == solicitud), None)
        if parada is None:
            raise DatosInvalidos(f"La solicitud {solicitud.id} no esta en este viaje")
        parada.marcar_fallida(incidente)
        self.registrar_incidente(incidente)

    def registrar_incidente(self, incidente):
        self._incidentes.append(incidente)
        # --- Consulta (dict): todo lo calculado de un viaje en un solo lugar ---

    def resumen(self):
        """Devuelve un diccionario con los resultados del viaje.
        Es una foto de solo lectura: no muta nada y cada llamada arma un dict nuevo."""
        return {
            "id": self._id,
            "fecha": self._fecha,
            "estado": self._estado.value,
            "transporte": self._itinerario.transporte.id,
            "deposito": self._itinerario.deposito.id,
            "cantidad_paradas": len(self._itinerario.paradas),
            "distancia_km": self.distancia_total(),
            "carga_peso": self.carga_peso(),
            "carga_volumen": self.carga_volumen(),
            "costo": self.costo(),
            "impacto_ambiental": self.impacto_ambiental(),
            "hora_regreso": self._itinerario.hora_regreso,
            "es_factible": self.es_factible(),
            "entregas": len(self._comprobantes),
            "incidentes": len(self._incidentes),
        }



    