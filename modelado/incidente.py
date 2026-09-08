from modelado.excepciones import DatosInvalidos
from modelado.enums import TipoIncidente


class Incidente:
    def __init__(self, id, tipo, fecha_hora, descripcion, afectado):
        if not isinstance(tipo, TipoIncidente):
            raise DatosInvalidos(f"tipo debe ser un TipoIncidente, no {tipo!r}")
        if not descripcion:
            raise DatosInvalidos("La descripcion del incidente no puede estar vacia")
        self.id = id
        self.tipo = tipo
        self.fecha_hora = fecha_hora
        self.descripcion = descripcion
        self.afectado = afectado
