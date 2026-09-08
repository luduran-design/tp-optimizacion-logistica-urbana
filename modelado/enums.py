from enum import Enum


class EstadoViaje(Enum):
    PLANIFICADO = "PLANIFICADO"
    EN_CURSO = "EN_CURSO"
    FINALIZADO = "FINALIZADO"


class TipoIncidente(Enum):
    DANIO = "DANIO"
    AUSENTE = "AUSENTE"
    RETRASO = "RETRASO"


class ResultadoParada(Enum):
    ENTREGADA = "ENTREGADA"
    FALLIDA = "FALLIDA"
