from modelado.excepciones import DatosInvalidos
from modelado.enums import TipoIncidente


class Incidente:
    """Anomalia registrada durante la ejecucion de un viaje.

    Todos sus atributos son inmutables desde afuera: una vez creado, un
    incidente es un registro que no se puede reescribir.
    """

    def __init__(self, id, tipo, fecha_hora, descripcion, afectado):
        if not isinstance(tipo, TipoIncidente):
            raise DatosInvalidos(f"tipo debe ser un TipoIncidente, no {tipo!r}")
        if not descripcion:
            raise DatosInvalidos("La descripcion del incidente no puede estar vacia")
        self._id = id
        self._tipo = tipo
        self._fecha_hora = fecha_hora
        self._descripcion = descripcion
        self._afectado = afectado

    @property
    def id(self):
        return self._id

    @property
    def tipo(self) -> TipoIncidente:
        return self._tipo

    @property
    def fecha_hora(self):
        return self._fecha_hora

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def afectado(self):
        return self._afectado
