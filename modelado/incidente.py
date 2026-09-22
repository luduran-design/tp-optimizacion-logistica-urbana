from datetime import datetime

from modelado.excepciones import DatosInvalidos
from modelado.enums import TipoIncidente
from modelado.solicitud import Solicitud
from modelado.transporte import Transporte


class Incidente:
    """Anomalia registrada durante la ejecucion de un viaje (regla 12).

    Tiene tipo (DANIO, AUSENTE o RETRASO), instante, descripcion no vacia y una
    referencia a la entidad afectada: una Solicitud o un Transporte. Es un
    registro: una vez creado no se puede reescribir. No modifica por si solo la
    planificacion; es Viaje quien decide que hacer con el.
    """

    def __init__(self, id, tipo, fecha_hora, descripcion, afectado):
        if not isinstance(id, str) or not id.strip():
            raise DatosInvalidos("El id del incidente debe ser un texto no vacio")
        if not isinstance(tipo, TipoIncidente):
            raise DatosInvalidos(f"tipo debe ser un TipoIncidente, no {tipo!r}")
        if not isinstance(fecha_hora, datetime):
            raise DatosInvalidos("La fecha y hora del incidente debe ser un datetime")
        if not isinstance(descripcion, str) or not descripcion.strip():
            raise DatosInvalidos("La descripcion del incidente no puede estar vacia")
        if not isinstance(afectado, (Solicitud, Transporte)):
            raise DatosInvalidos(
                f"El afectado debe ser una Solicitud o un Transporte, no {afectado!r}"
            )
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

    def afecta_a_solicitud(self) -> bool:
        return isinstance(self._afectado, Solicitud)

    def afecta_a_transporte(self) -> bool:
        return isinstance(self._afectado, Transporte)

    def __repr__(self):
        return f"Incidente('{self._id}', {self._tipo.value}, {self._afectado!r})"