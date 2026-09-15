from modelado.excepciones import DatosInvalidos, RutaIncompleta

class MatrizDistancias:
    def __init__(self, ubicaciones):
        self._ubicaciones = ubicaciones
        self._distancias = {}  # dict[(Ubicacion, Ubicacion)] -> float

    def distancia(self, origen, destino):
        if not self.contiene_tramo(origen, destino):
            raise RutaIncompleta(f"No existe tramo entre {origen} y {destino}")
        return self._distancias[(origen, destino)]

    def agregar_tramo(self, origen, destino, km):
        if km < 0:
            raise DatosInvalidos("La distancia no puede ser negativa")
        self._distancias[(origen, destino)] = km

    def contiene_tramo(self, origen, destino):
        return (origen, destino) in self._distancias
