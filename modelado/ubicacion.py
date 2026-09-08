from modelado.excepciones import DatosInvalidos


class Ubicacion:
    def __init__(self, id, nombre, descripcion):
        if not id:
            raise DatosInvalidos("El id de la ubicacion no puede ser vacio.")
        if not nombre:
            raise DatosInvalidos("El nombre de la ubicacion no puede ser vacio.")
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion

    def __eq__(self, otro):
        # Dos ubicaciones son iguales si tienen el mismo id (regla 1), no por ser el mismo
        # objeto en memoria.
        if not isinstance(otro, Ubicacion):
            return NotImplemented
        return self.id == otro.id

    def __hash__(self):
        # Mismo id, mismo hash, para poder usar Ubicacion como clave en la matriz de distancias.
        return hash(self.id)

    def __repr__(self):
        # Representacion legible: en errores y tests se ve Ubicacion('U1') en vez de
        # <Ubicacion object at 0x...>.
        return f"Ubicacion('{self.id}')"

    # Todo esto que se hizo aca tambien se aplica para solicitud, articulo y transporte
    def es_deposito(self):
        return False
