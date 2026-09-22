from modelado.excepciones import DatosInvalidos


class Articulo:
    """Unidad de carga: un producto identificado por id, con peso y volumen positivos.

    Todos sus atributos son inmutables desde afuera (properties de solo lectura):
    las invariantes se validan una vez en el __init__ y no pueden violarse despues.
    """

    def __init__(self, id, nombre, peso, volumen):
        if not isinstance(id, str) or not id.strip():
            raise DatosInvalidos("El id del articulo debe ser un texto no vacio.")
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatosInvalidos("El nombre del articulo debe ser un texto no vacio.")
        for nombre_campo, valor in (("peso", peso), ("volumen", volumen)):
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                raise DatosInvalidos(f"El {nombre_campo} del articulo debe ser un numero.")
            if valor <= 0:
                raise DatosInvalidos(f"El {nombre_campo} del articulo debe ser positivo.")
        self._id = id
        self._nombre = nombre
        self._peso = peso
        self._volumen = volumen

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def peso(self):
        return self._peso

    @property
    def volumen(self):
        return self._volumen

    def __eq__(self, otro):
        if not isinstance(otro, Articulo):
            return NotImplemented
        return self._id == otro._id

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"Articulo('{self._id}')"