from modelado.excepciones import DatosInvalidos
from modelado.solicitud import Solicitud
from modelado.ventana import Ventana
from modelado.articulo import Articulo
from modelado.viaje import Viaje


class Empresa:
    def __init__(self, deposito, matriz):
        self._deposito = deposito
        self._matriz = matriz
        # Registros indexados por id: la unicidad (RN1) queda garantizada por la
        # estructura, no por una busqueda que alguien se puede olvidar de hacer.
        self._flota = {}         # {transporte_id: Transporte}
        self._viajes = {}        # {viaje_id: Viaje}
        self._solicitudes = {}   # {solicitud_id: Solicitud}

    @property
    def deposito(self):
        return self._deposito

    # Las properties siguen devolviendo listas: quien las usa no tiene por que
    # saber como estan guardadas por dentro.
    @property
    def flota(self):
        return list(self._flota.values())

    @property
    def viajes(self):
        return list(self._viajes.values())

    @property
    def solicitudes(self):
        return list(self._solicitudes.values())

    def solicitudes_pendientes(self):
        return [s for s in self._solicitudes.values() if not s.esta_asignada()]

    # --- Registro ---

    def registrar_transporte(self, transporte) -> None:
        if transporte.id in self._flota:
            raise DatosInvalidos(f"Ya existe un transporte con id '{transporte.id}'")
        self._flota[transporte.id] = transporte

    def registrar_solicitud(self, solicitud) -> None:
        if solicitud.id in self._solicitudes:
            raise DatosInvalidos(f"Ya existe una solicitud con id '{solicitud.id}'")
        self._solicitudes[solicitud.id] = solicitud

    def crear_solicitud(self, id, destino, ventana_inicio, ventana_fin, **articulos):
        # **articulos recibe cada articulo como nombre=(peso, volumen), asi el
        # codigo cliente no necesita armar la lista de Articulo de antemano.
        if not articulos:
            raise DatosInvalidos("Una solicitud necesita al menos un articulo (RN2)")
        if id in self._solicitudes:
            raise DatosInvalidos(f"Ya existe una solicitud con id '{id}'")

        lista = []
        for nombre, medidas in articulos.items():
            try:
                peso, volumen = medidas
            except (TypeError, ValueError):
                raise DatosInvalidos(
                    f"El articulo '{nombre}' debe recibir (peso, volumen), "
                    f"se recibio {medidas!r}") from None
            lista.append(Articulo(f"{id}-{nombre}", nombre, peso, volumen))

        solicitud = Solicitud(id, destino, Ventana(ventana_inicio, ventana_fin), lista)
        self._solicitudes[id] = solicitud
        return solicitud

    # --- Consulta directa por id ---

    def buscar_solicitud(self, id):
        if id not in self._solicitudes:
            raise DatosInvalidos(f"No existe una solicitud con id '{id}'")
        return self._solicitudes[id]

    def buscar_transporte(self, id):
        if id not in self._flota:
            raise DatosInvalidos(f"No existe un transporte con id '{id}'")
        return self._flota[id]

    def buscar_viaje(self, id):
        if id not in self._viajes:
            raise DatosInvalidos(f"No existe un viaje con id '{id}'")
        return self._viajes[id]

    # --- Factory ---

    def crear_viaje(self, id_viaje, fecha, transporte, hora_salida):
        # Factory: nadie construye un Viaje sin pasar por aca.
        if id_viaje in self._viajes:
            raise DatosInvalidos(f"Ya existe un viaje con id '{id_viaje}'")

        viaje = Viaje(id_viaje, fecha, transporte,
                      self._deposito, self._matriz, hora_salida)
        self._viajes[id_viaje] = viaje
        return viaje

    def consultar_politica(self, politica, solicitudes):
        return politica.sugerir_orden(self._deposito, solicitudes, self._matriz)