class ErrorLogistica(Exception):
    """Raiz de todas las excepciones del dominio logistico."""


class DatosInvalidos(ErrorLogistica):
    """Dato faltante, vacio, negativo o de tipo incorrecto."""


class CapacidadExcedida(ErrorLogistica):
    """La carga supera la capacidad del transporte."""


class RutaIncompleta(ErrorLogistica):
    """Falta un tramo en la matriz de distancias."""


class VentanaIncumplida(ErrorLogistica):
    """La llegada cae fuera de la ventana horaria."""


class TransicionIlegal(ErrorLogistica):
    """Transicion de estado no permitida."""
