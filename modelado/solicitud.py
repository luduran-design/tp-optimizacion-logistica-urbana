from modelado.excepciones import DatosInvalidos, TransicionIlegal
from modelado.ubicacion import Ubicacion
from modelado.ventana import Ventana
from modelado.articulo import Articulo


class Solicitud:
    """Pedido de entrega: articulos a llevar a un destino dentro de una ventana horaria.

    id, destino, ventana y articulos son inmutables desde afuera. La lista de
    articulos se devuelve como copia (regla 2: el peso/volumen de una solicitud
    no puede modificarse luego de incorporarla a un viaje).
    """

    def __init__(self, id, destino, ventana, articulos):
        if not isinstance(id, str) or not id.strip():
            raise DatosInvalidos("El id de la solicitud debe ser un texto no vacio.")
        # isinstance tambien rechaza None, asi que reemplaza al chequeo de is None.
        if not isinstance(destino, Ubicacion):
            raise DatosInvalidos("El destino debe ser una Ubicacion.")
        if not isinstance(ventana, Ventana):
            raise DatosInvalidos("La ventana debe ser una Ventana.")
        if not isinstance(articulos, (list, tuple)) or not articulos:
            raise DatosInvalidos("La solicitud debe tener una lista con al menos un articulo.")
        for a in articulos:
            if not isinstance(a, Articulo):
                raise DatosInvalidos("Todos los elementos de articulos deben ser Articulo.")
        self._id = id
        self._destino = destino
        self._ventana = ventana
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
        if self._asignada:
            raise TransicionIlegal(f"La solicitud {self._id} ya esta asignada.")
        self._asignada = True

    def desmarcar_como_asignada(self):
        if not self._asignada:
            raise TransicionIlegal(f"La solicitud {self._id} no esta asignada.")
        self._asignada = False
