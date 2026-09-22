from modelado.parada import Parada
from modelado.excepciones import CapacidadExcedida, DatosInvalidos


class Itinerario:
    def __init__(self, deposito, hora_salida, matriz, transporte):
        self._deposito = deposito
        self._hora_salida = hora_salida
        self._matriz = matriz
        self._transporte = transporte
        self._paradas = []
        self._distancia_total = 0.0
        self._hora_regreso = None

    @property
    def paradas(self):
        return list(self._paradas)

    @property
    def distancia_total(self) -> float:
        return self._distancia_total

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
        return self._transporte.admite_carga(self.carga_peso(), self.carga_volumen())

    def costo(self) -> float:
        return self._transporte.calcular_costo(
            self._distancia_total, len(self._paradas)
        )

    def impacto(self) -> float:
        # Llamada polimorfica: SIEMPRE pasa la carga.
        # Cada transporte decide si la usa o no.
        return self._transporte.calcular_impacto(
            self._distancia_total, self.carga_peso()
        )

    def _calcular_distancia(self, paradas) -> float:
        """Calcula la distancia total de una secuencia propuesta de paradas.

        Es una funcion pura: no toca el estado del itinerario. Se usa para
        validar una propuesta antes de aplicarla. Puede lanzar RutaIncompleta
        si la matriz no cubre algun tramo de la secuencia.
        """
        if not paradas:
            return 0.0
        total = 0.0
        anterior = self._deposito
        for p in paradas:
            total += self._matriz.distancia(anterior, p.solicitud.destino)
            anterior = p.solicitud.destino
        total += self._matriz.distancia(anterior, self._deposito)
        return total

    def _verificar_capacidad(self, paradas) -> None:
        """Verifica que la carga total de la secuencia entre en el transporte.

        Lanza CapacidadExcedida con el peso y volumen concretos si no entra.
        """
        peso = sum(p.solicitud.peso_total() for p in paradas)
        volumen = sum(p.solicitud.volumen_total() for p in paradas)
        if not self._transporte.admite_carga(peso, volumen):
            raise CapacidadExcedida(
                f"La carga total (peso {peso}, volumen {volumen}) excede la "
                f"capacidad del transporte {self._transporte.id}"
            )

    def agregar(self, solicitud) -> None:
        """Agrega una solicitud al final del itinerario, si todas las reglas se cumplen.

        Valida en este orden:
          - regla 5: la solicitud no esta asignada a otro viaje ni duplicada aca;
          - regla 2: el destino no es el deposito;
          - regla 3: la ruta tiene todos los tramos necesarios;
          - regla 4: la carga total no excede la capacidad del transporte.
        Si cualquier chequeo falla, no se modifica ni la secuencia ni la distancia
        (regla 7). Solo al pasar todos los chequeos se aplica la propuesta y se
        marca la solicitud como asignada.
        """
        # Regla 5: una solicitud no puede pertenecer a dos viajes activos a la vez,
        # ni aparecer dos veces en el mismo itinerario. Una solicitud entregada
        # queda con el flag _asignada en True para siempre (ver Viaje.finalizar),
        # por lo que el primer chequeo tambien bloquea la replanificacion.
        if solicitud.esta_asignada():
            raise DatosInvalidos(
                f"La solicitud {solicitud.id} ya pertenece a un viaje activo "
                f"o ya fue entregada"
            )
        if any(p.solicitud == solicitud for p in self._paradas):
            raise DatosInvalidos(
                f"La solicitud {solicitud.id} ya esta en este itinerario"
            )
        # Regla 2: el destino no puede ser el deposito. Se compara por id, asi
        # que tambien atrapa una Ubicacion comun que tenga el mismo id del deposito.
        if solicitud.destino == self._deposito:
            raise DatosInvalidos(
                f"El destino de la solicitud {solicitud.id} no puede ser el deposito"
            )
        propuesta = self._paradas + [Parada(len(self._paradas) + 1, solicitud, None)]
        distancia = self._calcular_distancia(propuesta)   # puede lanzar RutaIncompleta
        self._verificar_capacidad(propuesta)              # puede lanzar CapacidadExcedida
        self._paradas = propuesta
        self._distancia_total = distancia
        solicitud.marcar_como_asignada()

    def quitar(self, solicitud) -> None:
        """Quita una solicitud del itinerario y renumera las paradas restantes.

        Lanza DatosInvalidos si la solicitud no esta en el itinerario. Al quitarla,
        la solicitud queda desmarcada como asignada y puede volver a planificarse
        en otro viaje.
        """
        parada = next((p for p in self._paradas if p.solicitud == solicitud), None)
        if parada is None:
            raise DatosInvalidos(
                f"La solicitud {solicitud.id} no esta en el itinerario"
            )
        propuesta = [p for p in self._paradas if p is not parada]
        distancia = self._calcular_distancia(propuesta)
        for i, p in enumerate(propuesta):
            p.actualizar_orden(i + 1)
        self._paradas = propuesta
        self._distancia_total = distancia
        solicitud.desmarcar_como_asignada()

    def reordenar(self, secuencia) -> None:
        """Reordena las paradas segun una permutacion de las mismas solicitudes.

        La secuencia recibida debe contener exactamente las mismas solicitudes
        que ya estan en el itinerario, ni una mas ni una menos, y sin repetir.
        Si no se cumple, lanza DatosInvalidos indicando cual es la diferencia.
        """
        # Primero el largo: la comparacion por conjuntos no detecta repetidos,
        # porque {s1, s1, s2} es igual a {s1, s2}.
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
        mapa = {p.solicitud: p for p in self._paradas}
        propuesta = [mapa[s] for s in secuencia]
        distancia = self._calcular_distancia(propuesta)
        for i, p in enumerate(propuesta):
            p.actualizar_orden(i + 1)
        self._paradas = propuesta
        self._distancia_total = distancia