from abc import ABC, abstractmethod 
# ABC + abstractmethod: permiten declarar clases "molde" que no se pueden instanciar solas 
# y obligan a las subclases a implementar ciertos metodos.

class Ubicacion:
    def __init__(self, id, nombre, descripcion):
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

class Articulo:
    def __init__(self, id, nombre, peso, volumen):
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
        self.inicio = inicio
        self.fin = fin

    def llega_tarde(self, instante):
        pass

    def inicio_de_servicio(self, llegada):
        pass

class Solicitud:
    def __init__(self, id, destino, ventana, articulos):
        self.id = id
        self.destino = destino
        self.ventana = ventana
        self.articulos = articulos
        
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
        pass

    def volumen_total(self):
        pass

    def llega_tarde(self, instante):
        pass

    def espera_desde(self, llegada):
        pass

class Transporte(ABC):
# Transporte es abstracta (ABC): "un transporte" a secas no existe, siempre es Moto, 
# Furgoneta o Camion. No se puede instanciar sola.
    def __init__(self, id, capacidad_peso, capacidad_volumen, velocidad_media,
                 costo_por_km, costo_por_parada, factor_ambiental):
        
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
    def calcular_impacto(self, kilometros):
        pass
    # Estos 3 metodos NO son abstractos: son iguales para todos los transportes, se implementan aca 
    # una sola vez y las subclases los heredan.
    def tiempo_de_tramo(self, kilometros):
        pass

    def admite_carga(self, peso, volumen):
        pass

    def calcular_costo(self, kilometros, cantidad_paradas):
        pass
    
class Motocicleta(Transporte):
    def calcular_impacto(self, kilometros):
        pass


class Furgoneta(Transporte):
    def calcular_impacto(self, kilometros):
        pass


class Camion(Transporte):
    def calcular_impacto(self, kilometros):
        pass

class Parada:
    def __init__(self, orden, solicitud, llegada_prevista, resultado):
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
    
    # variables para poder aplicar en el estado del viaje
    PLANIFICADO = "PLANIFICADO"
    EN_CURSO = "EN_CURSO"
    FINALIZADO = "FINALIZADO"
    
    def __init__(self, id_viaje, fecha, transporte, deposito, matriz, hora_salida):
        self._id = id_viaje
        self._fecha = fecha
        self._transporte = transporte
        self._deposito = deposito
        self._matriz = matriz
        self._hora_salida = hora_salida
        self._estado = Viaje.PLANIFICADO #el estado del viaje siempre debe empezar como planificado
        #listas exclusivamente del viaje, imposible de tocar desde afuera
        self._paradas = []
        self._comprobantes = []
        self._incidentes = []

    # devuelven una copia de cada lista para que quien las lee no pueda modificar la interna
    @property
    def paradas(self):
        return list(self._paradas)

    @property
    def comprobantes(self):
        return list(self._comprobantes)

    @property
    def incidentes(self):
        return list(self._incidentes)
    
    def distancia_entre(self, origen, destino):
        pass

    def recorrer(self):
        pass

    def es_factible(self):
        pass

    def carga_peso(self):
        pass

    def carga_volumen(self):
        pass

    def distancia_total(self):
        pass

    def costo(self):
        pass

    def impacto_ambiental(self):
        pass

    def esta_completo(self):
        pass

    def parada_actual(self):
        pass

    def agregar_solicitud(self, solicitud):
        pass

    def quitar_solicitud(self, solicitud):
        pass

    def reordenar(self, secuencia):
        pass

    def iniciar(self):
        pass

    def registrar_entrega(self, solicitud, receptor, fecha_hora):
        pass

    def registrar_fallo(self, solicitud, incidente):
        pass

    def registrar_incidente(self, incidente):
        pass

    def finalizar(self):
        pass

class Comprobante:
    def __init__(self, nro, solicitud, fecha_hora_real, receptor):
        self.nro = nro
        self.solicitud = solicitud
        self.fecha_hora_real = fecha_hora_real
        self.receptor = receptor

class Incidente:
    def __init__(self, id, tipo, fecha_hora, descripcion, afectado):
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
