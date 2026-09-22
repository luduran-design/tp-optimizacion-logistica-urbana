from datetime import datetime, timedelta

from modelado.parada import Parada
from modelado.deposito import Deposito
from modelado.matriz_distancias import MatrizDistancias
from modelado.transporte import Transporte
from modelado.solicitud import Solicitud
from modelado.excepciones import (
    CapacidadExcedida, DatosInvalidos, RutaIncompleta, VentanaIncumplida
)


class Itinerario:
    TIEMPO_DE_SERVICIO = timedelta(minutes=10)  # regla 6

    def __init__(self, deposito, hora_salida, matriz, transporte):
        if not isinstance(deposito, Deposito):
            raise DatosInvalidos("El deposito debe ser un Deposito.")
        if not isinstance(hora_salida, datetime):
            raise DatosInvalidos("La hora de salida debe ser un datetime.")
        if not isinstance(matriz, MatrizDistancias):
            raise DatosInvalidos("La matriz debe ser una MatrizDistancias.")
        if not matriz.contiene_ubicacion(deposito):
            raise DatosInvalidos("El deposito no pertenece a la matriz.")
        if not isinstance(transporte, Transporte):
            raise DatosInvalidos("El transporte debe ser un Transporte.")
        self._deposito = deposito
        self._hora_salida = hora_salida
        self._matriz = matriz
        self._transporte = transporte
        self._paradas = []
        self._distancia_total = 0.0
        # Sin paradas, el transporte "vuelve" en el mismo momento en que sale.
        self._hora_regreso = hora_salida

    @property
    def paradas(self):
        return list(self._paradas)

    @property
    def distancia_total(self) -> float:
        return self._distancia_total

    @property
    def hora_salida(self):
        return self._hora_salida

    @property
    def hora_regreso(self):
        return self._hora_regreso

    @property
    def transporte(self):
        return self._transporte

    @property
    def deposito(self):
        return self._deposito

    def carga_peso(self) -> float:
        return sum(p.solicitud.peso_total() for p in self._paradas)

    def carga_volumen(self) -> float:
        return sum(p.solicitud.volumen_total() for p in self._paradas)

    def es_factible(self) -> bool:
        # Consulta: prueba capacidad y recorrido completo sin modificar nada.
        solicitudes = [p.solicitud for p in self._paradas]
        try:
            self._verificar_capacidad(solicitudes)
            self._calcular_recorrido(solicitudes)
        except (CapacidadExcedida, RutaIncompleta, VentanaIncumplida):
            return False
        return True

    def costo(self) -> float:
        return self._transporte.calcular_costo(
            self._distancia_total, len(self._paradas)
        )

    def impacto(self) -> float:
        # Llamada polimorfica: SIEMPRE pasa la carga. Cada transporte decide si la usa.
        return self._transporte.calcular_impacto(
            self._distancia_total, self.carga_peso()
        )

    def _verificar_capacidad(self, solicitudes) -> None:
        peso = sum(s.peso_total() for s in solicitudes)
        volumen = sum(s.volumen_total() for s in solicitudes)
        if not self._transporte.admite_carga(peso, volumen):
            raise CapacidadExcedida(
                f"La carga total (peso {peso}, volumen {volumen}) excede la "
                f"capacidad del transporte {self._transporte.id}"
            )

    def _calcular_recorrido(self, solicitudes):
        """Recorre la secuencia desde el deposito (regla 6). Funcion pura: no toca el estado.

        Devuelve (distancia_total, llegadas, hora_regreso).
        Lanza RutaIncompleta si falta un tramo o VentanaIncumplida si una llegada
        supera el fin de su ventana.
        """
        distancia = 0.0
        llegadas = []
        anterior = self._deposito
        salida = self._hora_salida
        for s in solicitudes:
            km = self._matriz.distancia(anterior, s.destino)
            distancia += km
            llegada = salida + self._transporte.tiempo_de_tramo(km)
            if s.llega_tarde(llegada):
                raise VentanaIncumplida(
                    f"La solicitud {s.id} llega a las {llegada:%H:%M}, "
                    f"despues del cierre de su ventana ({s.ventana.fin:%H:%M})"
                )
            llegadas.append(llegada)
            # Si llega antes espera al inicio; despues suma el servicio y sale.
            salida = s.espera_desde(llegada) + self.TIEMPO_DE_SERVICIO
            anterior = s.destino
        # Regreso al deposito: suma distancia y tiempo, sin ventana.
        km = self._matriz.distancia(anterior, self._deposito)
        distancia += km
        hora_regreso = salida + self._transporte.tiempo_de_tramo(km)
        return distancia, llegadas, hora_regreso

    def _aplicar(self, paradas, distancia, llegadas, hora_regreso) -> None:
        """Unico lugar que modifica el estado; solo se llama con una propuesta ya validada."""
        for i, p in enumerate(paradas):
            p.actualizar_orden(i + 1)
            p.actualizar_llegada(llegadas[i])
        self._paradas = paradas
        self._distancia_total = distancia
        self._hora_regreso = hora_regreso

    def agregar(self, solicitud) -> None:
        if not isinstance(solicitud, Solicitud):
            raise DatosInvalidos("Solo se pueden agregar objetos Solicitud.")
        # Regla 5: no asignada a otro viaje ni repetida aca.
        if solicitud.esta_asignada():
            raise DatosInvalidos(
                f"La solicitud {solicitud.id} ya pertenece a un viaje activo "
                f"o ya fue entregada"
            )
        if any(p.solicitud == solicitud for p in self._paradas):
            raise DatosInvalidos(
                f"La solicitud {solicitud.id} ya esta en este itinerario"
            )
        # Regla 2: el destino no puede ser el deposito.
        if solicitud.destino == self._deposito:
            raise DatosInvalidos(
                f"El destino de la solicitud {solicitud.id} no puede ser el deposito"
            )
        # Regla 7: primero se valida toda la propuesta; si algo falla, no se toca nada.
        solicitudes = [p.solicitud for p in self._paradas] + [solicitud]
        self._verificar_capacidad(solicitudes)                     # regla 4
        distancia, llegadas, hora_regreso = self._calcular_recorrido(solicitudes)  # reglas 3 y 6
        nueva = Parada(len(solicitudes), solicitud, llegadas[-1])
        self._aplicar(self._paradas + [nueva], distancia, llegadas, hora_regreso)
        solicitud.marcar_como_asignada()

    def quitar(self, solicitud) -> None:
        parada = next((p for p in self._paradas if p.solicitud == solicitud), None)
        if parada is None:
            raise DatosInvalidos(
                f"La solicitud {solicitud.id} no esta en el itinerario"
            )
        propuesta = [p for p in self._paradas if p is not parada]
        distancia, llegadas, hora_regreso = self._calcular_recorrido(
            [p.solicitud for p in propuesta]
        )
        self._aplicar(propuesta, distancia, llegadas, hora_regreso)
        solicitud.desmarcar_como_asignada()

    def reordenar(self, secuencia) -> None:
        if not isinstance(secuencia, (list, tuple)):
            raise DatosInvalidos("La secuencia debe ser una lista de solicitudes.")
        for s in secuencia:
            if not isinstance(s, Solicitud):
                raise DatosInvalidos("La secuencia solo puede contener Solicitud.")
        # Primero el largo: la comparacion por conjuntos no detecta repetidos.
        if len(secuencia) != len(self._paradas):
            raise DatosInvalidos(
                f"La secuencia tiene {len(secuencia)} solicitudes y el itinerario "
                f"{len(self._paradas)}: no puede haber repetidas ni faltantes"
            )
        actuales = {p.solicitud for p in self._paradas}
        nuevas = set(secuencia)
        if actuales != nuevas:
            faltan = {s.id for s in actuales - nuevas}
            sobran = {s.id for s in nuevas - actuales}
            raise DatosInvalidos(
                f"La secuencia debe contener las mismas solicitudes del itinerario. "
                f"Faltan: {faltan or 'ninguna'}. Sobran: {sobran or 'ninguna'}"
            )
        distancia, llegadas, hora_regreso = self._calcular_recorrido(list(secuencia))
        mapa = {p.solicitud: p for p in self._paradas}
        self._aplicar([mapa[s] for s in secuencia], distancia, llegadas, hora_regreso)