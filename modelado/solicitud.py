from modelado.excepciones import DatosInvalidos


class Solicitud:
    def __init__(self, id, destino, ventana, articulos):
        if not id:
            raise DatosInvalidos("El id de la solicitud no puede ser vacio")
        if destino is None:
            raise DatosInvalidos("La solicitud debe tener un destino")
        # is None en vez de not: preguntamos si falta el objeto, no su valor de verdad.
        if ventana is None:
            raise DatosInvalidos("La solicitud debe tener una ventana horaria")
        if not articulos:
            raise DatosInvalidos("La solicitud debe tener al menos un articulo")
        self.id = id
        self.destino = destino
        self.ventana = ventana
        self.articulos = articulos
        self._asignada = False

    def __eq__(self, otro):
        if not isinstance(otro, Solicitud):
            return NotImplemented
        return self.id == otro.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"Solicitud('{self.id}')"

    # Dejamos los 4 metodos aca que tambien estaban en articulo porque solicitud suma el
    # peso/volumen de sus articulos (regla 2) y delega los horarios en su Ventana.
    # Articulo es solo una unidad de carga.
    def peso_total(self):
        return sum(a.peso for a in self.articulos)

    def volumen_total(self):
        return sum(a.volumen for a in self.articulos)

    def llega_tarde(self, instante):
        pass

    def espera_desde(self, llegada):
        pass

    def esta_asignada(self):
        return self._asignada

    def marcar_como_asignada(self):
        self._asignada = True

    def desmarcar_como_asignada(self):
        self._asignada = False
