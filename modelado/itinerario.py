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

    def carga_peso(self) -> float:
        return sum(p.solicitud.peso_total() for p in self._paradas)

    def carga_volumen(self) -> float:
        return sum(p.solicitud.volumen_total() for p in self._paradas)

    def agregar(self, solicitud) -> None:
        # Regla 7: si al recalcular queda no factible, revertir todo cambio.
        pass

    def es_factible(self) -> bool:
        pass

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
