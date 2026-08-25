class Ubicacion:
    def __init__(self, id, nombre, descripcion):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        

    def es_igual_a(self, otra):
        pass

class Articulo:
    def __init__(self, id, nombre, peso, volumen):
        self.id = id
        self.nombre = nombre
        self.peso = peso
        self.volumen = volumen               
        
    def peso_total(self):
        pass

    def volumen_total(self):
        pass

    def llega_tarde(self, instante):
        pass

    def espera_desde(self, llegada):
        pass

class Solicitud:
    def __init__(self, id, destino, ventana, articulos):
        self.id = id
        self.destino = destino
        self.ventana = ventana
        self.articulos = articulos
    def peso_total(self):
        pass

    def volumen_total(self):
        pass

    def llega_tarde(self, instante):
        pass

    def espera_desde(self, llegada):
        pass

class Transporte():
    def __init__(self, id, capacidad_peso, capacidad_volumen, velocidad_media,
                 costo_por_km, costo_por_parada, factor_ambiental):
        
        self.id = id
        self.capacidad_peso = capacidad_peso
        self.capacidad_volumen = capacidad_volumen
        self.velocidad_media = velocidad_media
        self.costo_por_km = costo_por_km
        self.costo_por_parada = costo_por_parada
        self.factor_ambiental = factor_ambiental

    def calcular_impacto(self, kilometros):
        pass

    def tiempo_de_tramo(self, kilometros):
        pass

    def admite_carga(self, peso, volumen):
        pass

    def calcular_costo(self, kilometros, cantidad_paradas):
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
    def __init__(self, id, fecha, transporte, deposito, matriz, hora_salida,
                 estado, paradas, comprobantes, incidentes):
        self.id = id
        self.fecha = fecha
        self.transporte = transporte
        self.deposito = deposito
        self.matriz = matriz
        self.hora_salida = hora_salida
        self.estado = estado
        self.paradas = paradas
        self.comprobantes = comprobantes
        self.incidentes = incidentes

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

class PoliticaDeOrdenamiento():
    def __init__(self, nombre):
        self.nombre = nombre

    def sugerir_orden(self, deposito, solicitudes, matriz):
        pass
