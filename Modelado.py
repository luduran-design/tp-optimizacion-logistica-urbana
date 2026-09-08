from abc import ABC, abstractmethod 
# ABC + abstractmethod: permiten declarar clases "molde" que no se pueden instanciar solas 
# y obligan a las subclases a implementar ciertos metodos.

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


class ErrorLogistica(Exception):
    """Raiz de todas las excepciones del dominio logistico."""
    pass

class DatosInvalidos(ErrorLogistica):
    """Dato faltante, vacio, negativo o de tipo incorrecto."""
    pass

class CapacidadExcedida(ErrorLogistica):
    """La carga supera la capacidad del transporte."""
    pass

class RutaIncompleta(ErrorLogistica):
    """Falta un tramo en la matriz de distancias."""
    pass

class VentanaIncumplida(ErrorLogistica):
    """La llegada cae fuera de la ventana horaria."""
    pass

class TransicionIlegal(ErrorLogistica):
    """Transicion no permitida en la maquina de estados del Viaje."""
    pass


class Ubicacion:
    def __init__(self, id, nombre, descripcion):
        if not id:
            raise DatosInvalidos("El id de la ubicacion no puede ser vacio.")
        if not nombre:
            raise DatosInvalidos("El nombre de la ubicacion no puede ser vacio.")
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        
    def __eq__(self, otro):
        # Dos ubicaciones son iguales si tienen el mismo id (regla 1), no por ser el mismo 
        # objeto en memoria.
        if not isinstance(otro, Ubicacion):
            return NotImplemented
        return self.id == otro.id

    def __hash__(self):
        # Mismo id, mismo hash, para poder usar Ubicacion como clave en la matriz de distancias.
        return hash(self.id)

    def __repr__(self):
         # Representacion legible: en errores y tests se ve Ubicacion('U1') en vez de 
         # <Ubicacion object at 0x...>.
        return f"Ubicacion('{self.id}')"
    
    # Todo esto que se hizo aca tambien se aplica para solicitud, articulo y transporte
    def es_deposito(self):
        return False

class Articulo:
    
    def __init__(self, id, nombre, peso, volumen):
        if not id:
            raise DatosInvalidos("El id del articulo no puede ser vacio")
        if not nombre:
            raise DatosInvalidos("El nombre del articulo no puede ser vacio")
        if peso <= 0:
            raise DatosInvalidos("El peso del articulo debe ser positivo")
        if volumen <= 0:
            raise DatosInvalidos("El volumen del articulo debe ser positivo")
        self.id = id
        self.nombre = nombre
        self.peso = peso
        self.volumen = volumen               
    
    def __eq__(self, otro):
        if not isinstance(otro, Articulo):
            return NotImplemented
        return self.id == otro.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"Articulo('{self.id}')"

# Ventana concentra la logica de horarios (inicio/fin). llega_tarde y inicio_de_servicio se 
# mudaron aca desde Articulo, que no debe saber de tiempos segun las reglas.
class Ventana:
    def __init__(self, inicio, fin):
        if inicio >= fin:
            raise DatosInvalidos("El inicio de la ventana debe ser anterior al fin")
        self.inicio = inicio
        self.fin = fin

    def llega_tarde(self, instante):
        pass

    def inicio_de_servicio(self, llegada):
        pass

class Solicitud:
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
        self.id = id
        self.destino = destino
        self.ventana = ventana
        self.articulos = articulos
        self._asignada = False
        
    def __eq__(self, otro):
        if not isinstance(otro, Solicitud):
            return NotImplemented
        return self.id == otro.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"Solicitud('{self.id}')"
    
    # Dejamos los 4 metodos aca que tambien estaban en articulo porque solicitud suma el 
    # peso/volumen de sus articulos (regla 2) y delega los horarios en su Ventana. 
    # Articulo es solo una unidad de carga.
    def peso_total(self):
        return sum(a.peso for a in self.articulos)

    def volumen_total(self):
        return sum(a.volumen for a in self.articulos)

    def llega_tarde(self, instante):
        pass

    def espera_desde(self, llegada):
        pass

    def esta_asignada(self):
        return self._asignada

    def marcar_como_asignada(self):
        self._asignada = True

    def desmarcar_como_asignada(self):
        self._asignada = False

class Transporte(ABC):
# Transporte es abstracta (ABC): "un transporte" a secas no existe, siempre es Moto, 
# Furgoneta o Camion. No se puede instanciar sola.
    def __init__(self, id, capacidad_peso, capacidad_volumen, velocidad_media,
                 costo_por_km, costo_por_parada, factor_ambiental):
        if not id:
            raise DatosInvalidos("El id del transporte no puede ser vacio")
        if capacidad_peso <= 0:
            raise DatosInvalidos("La capacidad de peso debe ser positiva")
        if capacidad_volumen <= 0:
            raise DatosInvalidos("La capacidad de volumen debe ser positiva")
        if velocidad_media <= 0:
            raise DatosInvalidos("La velocidad media debe ser positiva")
        # Costos y factor: cero es valido, negativo no.
        if costo_por_km < 0:
            raise DatosInvalidos("El costo por km no puede ser negativo")
        if costo_por_parada < 0:
            raise DatosInvalidos("El costo por parada no puede ser negativo")
        if factor_ambiental < 0:
            raise DatosInvalidos("El factor ambiental no puede ser negativo")
        self.id = id
        self.capacidad_peso = capacidad_peso
        self.capacidad_volumen = capacidad_volumen
        self.velocidad_media = velocidad_media
        self.costo_por_km = costo_por_km
        self.costo_por_parada = costo_por_parada
        self.factor_ambiental = factor_ambiental

    def __eq__(self, otro):
        if not isinstance(otro, Transporte):
            return NotImplemented
        return self.id == otro.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f"Transporte('{self.id}')"
    
    # Abstracto: cada subtipo DEBE definir su propia formula de impacto (regla 9).
    @abstractmethod
    def calcular_impacto(self, kilometros,carga_kg):
        """Contrato: todo transporte recibe km y carga transportada.
        Cada subtipo decide si usa la carga o la ignora."""
        pass
    # Estos 3 metodos NO son abstractos: son iguales para todos los transportes, se implementan aca 
    # una sola vez y las subclases los heredan.
    def tiempo_de_tramo(self, kilometros):
        pass

    def admite_carga(self, peso, volumen):
        return peso <= self.capacidad_peso and volumen <= self.capacidad_volumen


    def calcular_costo(self, kilometros, cantidad_paradas):
        pass
    
class Motocicleta(Transporte):
    PISO_ARRANQUE_FRIO = 0.5  # kg CO2 fijos por poner el motor en marcha (Atributo de clase)
    def calcular_impacto(self, kilometros,carga_kg):
        # Ignora carga: la moto no cambia significativamente su
        # emision segun cuanto lleve.

        # Costo fijo de arranque + costo lineal por km. En trayectos cortos
        # (el caso típico de una moto haciendo última milla), el piso fijo
        # pesa proporcionalmente más que en un trayecto largo — por eso NO
        # es lineal puro, tiene un término independiente de la distancia.
        return self.PISO_ARRANQUE_FRIO + kilometros * self.factor_ambiental



class Furgoneta(Transporte):
    def calcular_impacto(self, kilometros, carga_kg):
        # Caso base, lineal. Con los datos del ejemplo de aceptación del
        # enunciado (45 km, factor 0.27) da 12.15 kg CO2 — el número exacto
        # que trae el README, así que sirve para validar la fórmula con un test.
        return kilometros * self.factor_ambiental



class Camion(Transporte):
    def calcular_impacto(self, kilometros, carga_kg):
        # Un camión cargado contamina más que uno vacío: se agrega un factor
        # multiplicativo que crece según qué porcentaje de su capacidad va
        # transportando. carga_actual_kg tiene default 0 para que la llamada
        # polimórfica transporte.calcular_impacto(distancia) siga funcionando
        # igual sin importar el subtipo real (si no se pasa carga, se asume
        # que va vacío y se calcula el piso mínimo de impacto).
        factor_carga = 1 + (carga_kg / self.capacidad_peso)
        return kilometros * self.factor_ambiental * factor_carga


class Parada:
    def __init__(self, orden, solicitud, llegada_prevista, resultado):
        if not isinstance(resultado, ResultadoParada):
            raise DatosInvalidos(f"resultado debe ser un ResultadoParada, no {resultado!r}")
        self.orden = orden
        self.solicitud = solicitud
        self.llegada_prevista = llegada_prevista
        self.resultado = resultado
    def esta_pendiente(self):
        pass

    def entregar(self, receptor, fecha_hora):
        pass

    def marcar_fallida(self, incidente):
        pass

class Viaje:
    def __init__(self, id_viaje, fecha, transporte, deposito, matriz, hora_salida):
        self._id = id_viaje
        self._fecha = fecha
        self._estado = EstadoViaje.PLANIFICADO
        self._itinerario = Itinerario(deposito, hora_salida, matriz, transporte)
        self._comprobantes = []
        self._incidentes = []

    # --- Identidad y estado propios ---
    @property
    def id(self):
        return self._id

    @property
    def fecha(self):
        return self._fecha

    @property
    def estado(self) -> EstadoViaje:
        return self._estado

    @property
    def itinerario(self) -> "Itinerario":
        return self._itinerario

    @property
    def comprobantes(self):
        return list(self._comprobantes)

    @property
    def incidentes(self):
        return list(self._incidentes)

    # --- Delegacion al itinerario ---
    @property
    def paradas(self):
        return self._itinerario.paradas

    def distancia_total(self) -> float:
        return self._itinerario.distancia_total

    def carga_peso(self) -> float:
        return self._itinerario.carga_peso()

    def carga_volumen(self) -> float:
        return self._itinerario.carga_volumen()

    def es_factible(self) -> bool:
        return self._itinerario.es_factible()

    def costo(self) -> float:
        return self._itinerario.costo()

    def impacto_ambiental(self) -> float:
        return self._itinerario.impacto()

    def agregar_solicitud(self, solicitud):
        self._itinerario.agregar(solicitud)

    def quitar_solicitud(self, solicitud):
        pass

    def reordenar(self, secuencia):
        pass

    # --- Maquina de estados (regla 10) ---

    def iniciar(self):
        if self._estado != EstadoViaje.PLANIFICADO:
            raise TransicionIlegal(
                f"No se puede iniciar un viaje en estado {self._estado.value}"
            )
        self._estado = EstadoViaje.EN_CURSO

    def finalizar(self):
        if self._estado != EstadoViaje.EN_CURSO:
            raise TransicionIlegal(
                f"No se puede finalizar un viaje en estado {self._estado.value}"
            )
        self._estado = EstadoViaje.FINALIZADO

    def recorrer(self):
        pass

    def esta_completo(self):
        pass

    def parada_actual(self):
        pass

    def registrar_entrega(self, solicitud, receptor, fecha_hora):
        pass

    def registrar_fallo(self, solicitud, incidente):
        pass

    def registrar_incidente(self, incidente):
        self._incidentes.append(incidente)


class Comprobante:
    def __init__(self, nro, solicitud, fecha_hora_real, receptor):
        self.nro = nro
        self.solicitud = solicitud
        self.fecha_hora_real = fecha_hora_real
        self.receptor = receptor

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

class PoliticaDeOrdenamiento(ABC):
    # Politica abstracta (ABC): define el "contrato" que toda politica debe cumplir para 
    # ser intercambiable sin tocar el nucleo (regla 13)
    
    # Abstracto: cada politica concreta define su propio criterio de orden. 
    # Devuelve un orden sugerido, NO modifica ningun viaje (regla 13).
    @abstractmethod
    def sugerir_orden(self, deposito, solicitudes, matriz):
        pass
    
class VecinoMasCercano(PoliticaDeOrdenamiento):
        # VecinoMasCercano: ordena empezando por la solicitud mas cercana al deposito y 
        # siguiendo por la mas cercana a la anterior. Criterio distinto a MenorVentanaPrimero
        # (regla 13 pide 2 politicas que ordenen distinto).
        def sugerir_orden(self, deposito, solicitudes, matriz):
            pass

class MenorVentanaPrimero(PoliticaDeOrdenamiento):
        # MenorVentanaPrimero: ordena por la ventana horaria que cierra antes 
        # (las mas urgentes primero). Es la segunda politica intercambiable exigida por la 
        # regla 13.
        def sugerir_orden(self, deposito, solicitudes, matriz):
            pass

class Deposito(Ubicacion):
    def es_deposito(self) -> bool:
        return True

class MatrizDistancias:
    def __init__(self, ubicaciones):
        self._ubicaciones = ubicaciones
        self._distancias = {}  # dict[(Ubicacion, Ubicacion)] -> float

    def distancia(self, origen, destino) -> float:
        pass

    def agregar_tramo(self, origen, destino, km: float) -> None:
        pass

    def contiene_tramo(self, origen, destino) -> bool:
        pass

class Itinerario:
    def __init__(self, deposito, hora_salida, matriz, transporte):
        self._deposito = deposito
        self._hora_salida = hora_salida
        self._matriz = matriz
        self._transporte = transporte
        self._paradas = []
        self._distancia_total = 0.0
        self._hora_regreso = None

    @property
    def paradas(self):
        return list(self._paradas) 

    @property
    def distancia_total(self) -> float:
        return self._distancia_total

    @property
    def hora_regreso(self):
        return self._hora_regreso

    def carga_peso(self) -> float:
        return sum(p.solicitud.peso_total() for p in self._paradas)

    def carga_volumen(self) -> float:
        return sum(p.solicitud.volumen_total() for p in self._paradas)

    def agregar(self, solicitud) -> None:
        # Regla 7: si al recalcular queda no factible, revertir todo cambio.
        pass

    def es_factible(self) -> bool:
        pass

    def costo(self) -> float:
        return self._transporte.calcular_costo(
            self._distancia_total, len(self._paradas)
        )

    def impacto(self) -> float:
        # Llamada polimorfica: SIEMPRE pasa la carga.
        # Cada transporte decide si la usa o no.
        return self._transporte.calcular_impacto(
            self._distancia_total, self.carga_peso()
        )

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