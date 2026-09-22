from modelado.excepciones import DatosInvalidos, RutaIncompleta
from modelado.ubicacion import Ubicacion

class MatrizDistancias:
    """Tabla dirigida de distancias en km entre ubicaciones conocidas (regla 3).

    - Se construye con las ubicaciones que cubre; sus ids deben ser unicos (regla 1)
      y un tramo solo puede definirse entre ubicaciones conocidas.
    - Es dirigida: que exista A->B no implica que exista B->A.
    - La distancia de una ubicacion a si misma es siempre 0 y no hace falta cargarla.
    - Si falta un tramo, distancia() lanza RutaIncompleta y no modifica nada.
    """

    def __init__(self, ubicaciones):
        self._ubicaciones = {}   # {id: Ubicacion}
        for u in ubicaciones:
            if not isinstance(u, Ubicacion):
                raise DatosInvalidos(f"Elemento invalido en la matriz: {u!r}")
            if u.id in self._ubicaciones:
                raise DatosInvalidos(f"Ubicacion duplicada en la matriz: '{u.id}'")
            self._ubicaciones[u.id] = u
        self._distancias = {}    # {(origen, destino): km}

    @property
    def ubicaciones(self):
        return list(self._ubicaciones.values())

    def contiene_ubicacion(self, ubicacion) -> bool:
        # Si no es una Ubicacion, directamente no pertenece.
        return isinstance(ubicacion, Ubicacion) and ubicacion.id in self._ubicaciones


    def _exigir_conocida(self, ubicacion) -> None:
        if not self.contiene_ubicacion(ubicacion):
            raise DatosInvalidos(f"La ubicacion {ubicacion!r} no pertenece a la matriz")
        
    def agregar_tramo(self, origen, destino, km) -> None:
        self._exigir_conocida(origen)
        self._exigir_conocida(destino)
        if isinstance(km, bool) or not isinstance(km, (int, float)):
            raise DatosInvalidos("La distancia debe ser un numero.")
        if km < 0:
            raise DatosInvalidos("La distancia no puede ser negativa")
        if origen == destino and km != 0:
            raise DatosInvalidos("La distancia de una ubicacion a si misma es cero")
        self._distancias[(origen, destino)] = km

    def contiene_tramo(self, origen, destino) -> bool:
        return origen == destino or (origen, destino) in self._distancias

    def distancia(self, origen, destino) -> float:
        if origen == destino:
            return 0.0
        if (origen, destino) not in self._distancias:
            raise RutaIncompleta(f"No existe tramo entre {origen} y {destino}")
        return self._distancias[(origen, destino)]