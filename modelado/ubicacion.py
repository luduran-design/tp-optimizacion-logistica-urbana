from modelado.excepciones import DatosInvalidos


class Ubicacion:
    """Punto geografico con identidad por id (regla 1).

    Todos sus atributos son inmutables desde afuera. Dos ubicaciones son iguales
    si comparten id, aunque tengan nombre o descripcion distintos.
    """

    def __init__(self, id, nombre, descripcion):
        if not id:
            raise DatosInvalidos("El id de la ubicacion no puede ser vacio.")
        if not nombre:
            raise DatosInvalidos("El nombre de la ubicacion no puede ser vacio.")
        self._id = id
        self._nombre = nombre
        self._descripcion = descripcion

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def descripcion(self):
        return self._descripcion

    def __eq__(self, otro):
        # Dos ubicaciones son iguales si tienen el mismo id (regla 1), no por ser el mismo
        # objeto en memoria.
        if not isinstance(otro, Ubicacion):
            return NotImplemented
        return self._id == otro._id

    def __hash__(self):
        # Mismo id, mismo hash, para poder usar Ubicacion como clave en la matriz de distancias.
        return hash(self._id)

    def __repr__(self):
        # Representacion legible: en errores y tests se ve Ubicacion('U1') en vez de
        # <Ubicacion object at 0x...>.
        return f"Ubicacion('{self._id}')"

    def es_deposito(self) -> bool:
        return False
