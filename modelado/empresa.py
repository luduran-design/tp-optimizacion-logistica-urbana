from modelado.viaje import Viaje


class Empresa:
    def __init__(self, deposito, matriz):
        self._deposito = deposito
        self._matriz = matriz
        self._flota = []
        self._viajes = []
        self._solicitudes = []

    @property
    def deposito(self):
        return self._deposito

    @property
    def flota(self):
        return list(self._flota)

    @property
    def viajes(self):
        return list(self._viajes)

    @property
    def solicitudes(self):
        return list(self._solicitudes)

    def solicitudes_pendientes(self):
        return [s for s in self._solicitudes if not s.esta_asignada()]

    def registrar_transporte(self, transporte) -> None:
        self._flota.append(transporte)

    def registrar_solicitud(self, solicitud) -> None:
        self._solicitudes.append(solicitud)

    def crear_viaje(self, id_viaje, fecha, transporte, hora_salida):
        # Factory: nadie construye un Viaje sin pasar por aca.
        viaje = Viaje(id_viaje, fecha, transporte,
                      self._deposito, self._matriz, hora_salida)
        self._viajes.append(viaje)
        return viaje

    def consultar_politica(self, politica, solicitudes):
        return politica.sugerir_orden(self._deposito, solicitudes, self._matriz)
