from modelado.excepciones import DatosInvalidos


# Ventana concentra la logica de horarios (inicio/fin). llega_tarde y inicio_de_servicio se
# mudaron aca desde Articulo, que no debe saber de tiempos segun las reglas.
class Ventana:
    def __init__(self, inicio, fin):
        if inicio >= fin:
            raise DatosInvalidos("El inicio de la ventana debe ser anterior al fin")
        self.inicio = inicio
        self.fin = fin

    def llega_tarde(self, instante):
        pass

    def inicio_de_servicio(self, llegada):
        pass
