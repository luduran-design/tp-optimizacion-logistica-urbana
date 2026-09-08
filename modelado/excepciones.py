class ErrorLogistica(Exception):
    """Raiz de todas las excepciones del dominio logistico."""
    pass


class DatosInvalidos(ErrorLogistica):
    """Dato faltante, vacio, negativo o de tipo incorrecto."""
    pass


class CapacidadExcedida(ErrorLogistica):
    """La carga supera la capacidad del transporte."""
    pass


class RutaIncompleta(ErrorLogistica):
    """Falta un tramo en la matriz de distancias."""
    pass


class VentanaIncumplida(ErrorLogistica):
    """La llegada cae fuera de la ventana horaria."""
    pass


class TransicionIlegal(ErrorLogistica):
    """Transicion no permitida en la maquina de estados del Viaje."""
    pass
