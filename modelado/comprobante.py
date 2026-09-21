from modelado.excepciones import DatosInvalidos


class Comprobante:
    """Comprobante de entrega: registra quien recibio una solicitud, cuando, y bajo que numero.

    Es un objeto de datos del dominio: valida sus campos en el __init__ y una
    vez construido queda inmutable (todos los atributos son properties de solo
    lectura).
    """

    def __init__(self, nro, solicitud, fecha_hora_real, receptor):
        if nro is None or nro <= 0:
            raise DatosInvalidos(
                f"El nro del comprobante debe ser un entero positivo, no {nro!r}"
            )
        if solicitud is None:
            raise DatosInvalidos("El comprobante debe tener una solicitud")
        if fecha_hora_real is None:
            raise DatosInvalidos("El comprobante debe tener una fecha y hora reales")
        if not receptor:
            raise DatosInvalidos(
                "El receptor del comprobante no puede estar vacio"
            )
        self._nro = nro
        self._solicitud = solicitud
        self._fecha_hora_real = fecha_hora_real
        self._receptor = receptor

    @property
    def nro(self):
        return self._nro

    @property
    def solicitud(self):
        return self._solicitud

    @property
    def fecha_hora_real(self):
        return self._fecha_hora_real

    @property
    def receptor(self):
        return self._receptor
