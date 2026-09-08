"""Paquete modelado -- clases de dominio de LISASA.

Este __init__.py re-exporta todos los nombres publicos para que el resto
del codigo pueda hacer:

    from modelado import Viaje, Empresa, Furgoneta, EstadoViaje, ...

en lugar de tener que importar de cada archivo por separado:

    from modelado.viaje import Viaje
    from modelado.empresa import Empresa
    ...

Si agregas una clase nueva a `modelado/`, agregala tambien aca.
"""

# Excepciones
from modelado.excepciones import (
    ErrorLogistica,
    DatosInvalidos,
    CapacidadExcedida,
    RutaIncompleta,
    VentanaIncumplida,
    TransicionIlegal,
)

# Enums
from modelado.enums import (
    EstadoViaje,
    TipoIncidente,
    ResultadoParada,
)

# Ubicaciones y articulos
from modelado.ubicacion import Ubicacion
from modelado.deposito import Deposito
from modelado.articulo import Articulo
from modelado.ventana import Ventana
from modelado.solicitud import Solicitud

# Transportes
from modelado.transporte import Transporte
from modelado.motocicleta import Motocicleta
from modelado.furgoneta import Furgoneta
from modelado.camion import Camion

# Ejecucion
from modelado.parada import Parada
from modelado.comprobante import Comprobante
from modelado.incidente import Incidente

# Recorrido y viaje
from modelado.matriz_distancias import MatrizDistancias
from modelado.itinerario import Itinerario
from modelado.viaje import Viaje

# Politicas y empresa
from modelado.politica import (
    PoliticaDeOrdenamiento,
    VecinoMasCercano,
    MenorVentanaPrimero,
)
from modelado.empresa import Empresa
