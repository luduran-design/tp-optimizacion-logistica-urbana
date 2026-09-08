class MatrizDistancias:
    def __init__(self, ubicaciones):
        self._ubicaciones = ubicaciones
        self._distancias = {}  # dict[(Ubicacion, Ubicacion)] -> float

    def distancia(self, origen, destino) -> float:
        pass

    def agregar_tramo(self, origen, destino, km: float) -> None:
        pass

    def contiene_tramo(self, origen, destino) -> bool:
        pass
