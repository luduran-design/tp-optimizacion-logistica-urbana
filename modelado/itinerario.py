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

    def agregar(self, solicitud) -> None:
        # Regla 7: si al recalcular queda no factible, revertir todo cambio.
        pass

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
        
    def _recalcular_distancia(self):
        if not self._paradas:
            self._distancia_total = 0.0
            return
        total = 0.0
        anterior = self._deposito
        for p in self._paradas:
            total += self._matriz.distancia(anterior, p.solicitud.destino)
            anterior = p.solicitud.destino
        # Vuelta al deposito
        total += self._matriz.distancia(anterior, self._deposito)
        self._distancia_total = total

    def agregar(self, solicitud):
        # Guardar estado para poder revertir
        paradas_prev = list(self._paradas)
        distancia_prev = self._distancia_total

        # Intentar agregar
        nueva = Parada(len(self._paradas) + 1, solicitud, None)
        self._paradas.append(nueva)
        self._recalcular_distancia()

        # Si no es factible, revertir y avisar
        if not self.es_factible():
            self._paradas = paradas_prev
            self._distancia_total = distancia_prev
            raise CapacidadExcedida(
            f"La solicitud {solicitud.id} excede la capacidad del transporte"
        )

        solicitud.marcar_como_asignada()
        
    def quitar(self, solicitud):
        parada = next((p for p in self._paradas if p.solicitud == solicitud), None)
        if parada is None:
            raise DatosInvalidos(f"La solicitud {solicitud.id} no esta en el itinerario")
        self._paradas.remove(parada)
        # Renumerar las paradas restantes
        for i, p in enumerate(self._paradas):
            p.orden = i + 1
        self._recalcular_distancia()
        solicitud.desmarcar_como_asignada()
        
    def reordenar(self, secuencia):
        # Verificar que la secuencia tenga las mismas solicitudes
        actuales = {p.solicitud for p in self._paradas}
        nuevas = set(secuencia)
        if actuales != nuevas:
            raise DatosInvalidos("La secuencia debe contener las mismas solicitudes del itinerario")
        # Reordenar las paradas segun la secuencia
        mapa = {p.solicitud: p for p in self._paradas}
        self._paradas = [mapa[s] for s in secuencia]
        for i, p in enumerate(self._paradas):
            p.orden = i + 1
        self._recalcular_distancia()

