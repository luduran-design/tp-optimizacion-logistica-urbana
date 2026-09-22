from modelado.excepciones import DatosInvalidos
from datetime import datetime

# Ventana concentra la logica de horarios (inicio/fin). llega_tarde y inicio_de_servicio se
# mudaron aca desde Articulo, que no debe saber de tiempos segun las reglas.
class Ventana:
    def __init__(self, inicio, fin):
        if not isinstance(inicio, datetime) or not isinstance(fin, datetime):
            raise DatosInvalidos("Inicio y fin de la ventana deben ser datetime.")
        # Regla 2: inicio anterior o igual al fin (una ventana de un solo instante es valida).
        if inicio > fin:
            raise DatosInvalidos("El inicio de la ventana no puede ser posterior al fin.")
        self._inicio = inicio
        self._fin = fin

    @property
    def inicio(self):
        return self._inicio

    @property
    def fin(self):
        return self._fin

    def llega_tarde(self, instante):
        return instante > self._fin

    def inicio_de_servicio(self, llegada):
        return max(llegada, self._inicio)

    def __repr__(self):
        return f"Ventana({self._inicio}, {self._fin})"
