from modelado.excepciones import DatosInvalidos


# Ventana concentra la logica de horarios (inicio/fin). llega_tarde y inicio_de_servicio se
# mudaron aca desde Articulo, que no debe saber de tiempos segun las reglas.
class Ventana:
    def __init__(self, inicio, fin):
        for valor in (inicio, fin):
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                raise DatosInvalidos("Inicio y fin de la ventana deben ser numeros.")
            if valor < 0:
                raise DatosInvalidos("Inicio y fin de la ventana no pueden ser negativos.")
        if inicio >= fin:
            raise DatosInvalidos("El inicio de la ventana debe ser anterior al fin.")
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
