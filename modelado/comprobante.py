from modelado.excepciones import DatosInvalidos


class Comprobante:
    """Comprobante de entrega: registra quien recibio una solicitud, cuando, y bajo que numero.

    Es un objeto de datos del dominio: valida sus propios campos en el __init__
    y una vez construido queda inmutable en la practica (no expone setters).
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
        self.nro = nro
        self.solicitud = solicitud
        self.fecha_hora_real = fecha_hora_real
        self.receptor = receptor
