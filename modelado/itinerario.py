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
        if not paradas:
            return 0.0
        total = 0.0
        anterior = self._deposito
        for p in paradas:
            total += self._matriz.distancia(anterior, p.solicitud.destino)
            anterior = p.solicitud.destino
        total += self._matriz.distancia(anterior, self._deposito)
        return total

    def agregar(self, solicitud):
        propuesta = self._paradas + [Parada(len(self._paradas) + 1, solicitud, None)]
        distancia = self._calcular_distancia(propuesta)   # puede lanzar RutaIncompleta
        self._verificar_capacidad(propuesta)              # puede lanzar CapacidadExcedida
        self._paradas = propuesta
        self._distancia_total = distancia
        solicitud.marcar_como_asignada()
        
    def quitar(self, solicitud):
        parada = next((p for p in self._paradas if p.solicitud == solicitud), None)
        if parada is None:
            raise DatosInvalidos(f"La solicitud {solicitud.id} no esta en el itinerario")
        propuesta = [p for p in self._paradas if p is not parada]
        distancia = self._calcular_distancia(propuesta)
        for i, p in enumerate(propuesta):
            p.orden = i + 1
        self._paradas = propuesta
        self._distancia_total = distancia
        solicitud.desmarcar_como_asignada()


    def reordenar(self, secuencia):
        actuales = {p.solicitud for p in self._paradas}
        nuevas = set(secuencia)
        if actuales != nuevas:
            raise DatosInvalidos("La secuencia debe contener las mismas solicitudes del itinerario")
        mapa = {p.solicitud: p for p in self._paradas}
        propuesta = [mapa[s] for s in secuencia]
        distancia = self._calcular_distancia(propuesta)
        for i, p in enumerate(propuesta):
            p.orden = i + 1
        self._paradas = propuesta
        self._distancia_total = distancia

        
    def _verificar_capacidad(self, paradas) -> None:
        peso = sum(p.solicitud.peso_total() for p in paradas)
        volumen = sum(p.solicitud.volumen_total() for p in paradas)
        if not self._transporte.admite_carga(peso, volumen):
            raise CapacidadExcedida(
                "La solicitud excede la capacidad del transporte"
            )


        