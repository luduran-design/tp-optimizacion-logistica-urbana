from modelado.excepciones import DatosInvalidos


class Articulo:

    def __init__(self, id, nombre, peso, volumen):
        if not id:
            raise DatosInvalidos("El id del articulo no puede ser vacio")
        if not nombre:
            raise DatosInvalidos("El nombre del articulo no puede ser vacio")
        if peso <= 0:
            raise DatosInvalidos("El peso del articulo debe ser positivo")
        if volumen <= 0:
            raise DatosInvalidos("El volumen del articulo debe ser positivo")
        self.id = id
        self.nombre = nombre
        self.peso = peso
        self.volumen = volumen

    def __eq__(self, otro):
        if not isinstance(otro, Articulo):
            return NotImplemented
        return self.id == otro.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"Articulo('{self.id}')"
