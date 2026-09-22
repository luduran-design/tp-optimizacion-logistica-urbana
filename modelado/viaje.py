from modelado.enums import EstadoViaje
from modelado.excepciones import TransicionIlegal, DatosInvalidos
from modelado.itinerario import Itinerario
from modelado.comprobante import Comprobante
from modelado.incidente import Incidente
from modelado.solicitud import Solicitud
from modelado.transporte import Transporte


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
        # Decision de diseno (regla 5): al finalizar NO se llama a
        # solicitud.desmarcar_como_asignada() sobre las paradas entregadas.
        # El flag _asignada queda en True para siempre, de modo que un intento
        # posterior de agregar la solicitud a otro viaje sea rechazado por
        # Itinerario.agregar(). "Una solicitud entregada no puede volver a
        # planificarse" queda garantizado por esta invariante.
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

    # --- Ejecucion de paradas (regla 11) ---

    def _parada_para(self, solicitud):
        """Devuelve la parada actual si coincide con la solicitud pedida.

        Regla 11: las paradas se resuelven en el orden planificado. Solo se
        puede actuar sobre la proxima parada pendiente. Si la solicitud pedida
        no es la actual (fuera de orden, ajena al viaje, o ya cerrada), lanza
        TransicionIlegal explicando cual es la proxima.
        """
        actual = self.parada_actual()
        if actual is None:
            raise TransicionIlegal("El viaje no tiene paradas pendientes")
        if actual.solicitud != solicitud:
            raise TransicionIlegal(
                f"La proxima parada es {actual.solicitud.id}, no {solicitud.id}"
            )
        return actual

    def registrar_entrega(self, solicitud, receptor, fecha_hora):
        if self._estado != EstadoViaje.EN_CURSO:
            raise TransicionIlegal(
                "Solo se pueden registrar entregas en estado EN_CURSO"
            )
        parada = self._parada_para(solicitud)
        # Fabricamos el comprobante ANTES de cerrar la parada: si el receptor
        # es vacio, Comprobante lanza DatosInvalidos y la parada queda intacta.
        # Regla 7 aplicada tambien a esta transicion.
        comprobante = Comprobante(
            len(self._comprobantes) + 1, solicitud, fecha_hora, receptor
        )
        parada.entregar(receptor, fecha_hora)
        self._comprobantes.append(comprobante)

    def registrar_fallo(self, solicitud, incidente):
        if self._estado != EstadoViaje.EN_CURSO:
            raise TransicionIlegal(
                "Solo se pueden registrar fallos en estado EN_CURSO"
            )
        parada = self._parada_para(solicitud)
        # Regla 11: una parada fallida exige un incidente, y ese incidente tiene
        # que estar vinculado a la entrega afectada (la solicitud) o al transporte.
        # Se valida ANTES de cerrar la parada: si falla, no queda estado sucio.
        self._exigir_incidente_del_viaje(incidente)
        afectado = incidente.afectado
        if incidente.afecta_a_solicitud() and afectado != solicitud:
            raise DatosInvalidos(
                f"El incidente {incidente.id} afecta a {afectado.id}, "
                f"no a la solicitud {solicitud.id} que fallo"
            )
        parada.marcar_fallida(incidente)
        self._incidentes.append(incidente)

    # --- Incidentes (regla 12) ---

    def _exigir_incidente_del_viaje(self, incidente) -> None:
        """Regla 12: el incidente debe ser un Incidente y su afectado debe ser
        una solicitud de este viaje o el transporte de este viaje."""
        if not isinstance(incidente, Incidente):
            raise DatosInvalidos(f"Se esperaba un Incidente, no {incidente!r}")
        afectado = incidente.afectado
        if isinstance(afectado, Transporte):
            if afectado != self._itinerario.transporte:
                raise DatosInvalidos(
                    f"El transporte {afectado.id} no es el de este viaje"
                )
        elif isinstance(afectado, Solicitud):
            if all(p.solicitud != afectado for p in self._itinerario.paradas):
                raise DatosInvalidos(
                    f"La solicitud {afectado.id} no pertenece a este viaje"
                )

    def registrar_incidente(self, incidente):
        """Deja asentado un incidente del viaje sin cambiar el resultado de
        ninguna parada (regla 12: registrar no dispara cambios automaticos)."""
        self._exigir_incidente_del_viaje(incidente)
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