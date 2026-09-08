from abc import ABC, abstractmethod
# ABC + abstractmethod: permiten declarar clases "molde" que no se pueden instanciar solas
# y obligan a las subclases a implementar ciertos metodos.

from modelado.excepciones import DatosInvalidos


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
    def calcular_impacto(self, kilometros, carga_kg):
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
