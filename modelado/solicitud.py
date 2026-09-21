from modelado.excepciones import DatosInvalidos


class Solicitud:
    """Pedido de entrega: articulos a llevar a un destino dentro de una ventana horaria.

    id, destino, ventana y articulos son inmutables desde afuera. La lista de
    articulos se devuelve como copia (regla 2: el peso/volumen de una solicitud
    no puede modificarse luego de incorporarla a un viaje).
    """

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
        self._id = id
        self._destino = destino
        self._ventana = ventana
        # Copia defensiva: si quien nos paso la lista despues la muta, no nos afecta.
        self._articulos = list(articulos)
        self._asignada = False

    @property
    def id(self):
        return self._id

    @property
    def destino(self):
        return self._destino

    @property
    def ventana(self):
        return self._ventana

    @property
    def articulos(self):
        # Copia defensiva de salida: quien reciba la lista puede mutarla, pero
        # eso no cambia el estado interno de la solicitud.
        return list(self._articulos)

    def __eq__(self, otro):
        if not isinstance(otro, Solicitud):
            return NotImplemented
        return self._id == otro._id

    def __hash__(self):
        return hash(self._id)

    def __repr__(self):
        return f"Solicitud('{self._id}')"

    # Solicitud suma el peso/volumen de sus articulos (regla 2) y delega los horarios
    # en su Ventana. Articulo es solo una unidad de carga.
    def peso_total(self):
        return sum(a.peso for a in self._articulos)

    def volumen_total(self):
        return sum(a.volumen for a in self._articulos)

    def llega_tarde(self, instante):
        return self._ventana.llega_tarde(instante)

    def espera_desde(self, llegada):
        return self._ventana.inicio_de_servicio(llegada)

    def esta_asignada(self):
        return self._asignada

    def marcar_como_asignada(self):
        self._asignada = True

    def desmarcar_como_asignada(self):
        self._asignada = False
