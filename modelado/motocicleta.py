from modelado.transporte import Transporte


class Motocicleta(Transporte):
    PISO_ARRANQUE_FRIO = 0.5  # kg CO2 fijos por poner el motor en marcha (Atributo de clase)

    def calcular_impacto(self, kilometros, carga_kg):
        # Ignora carga: la moto no cambia significativamente su
        # emision segun cuanto lleve.

        # Costo fijo de arranque + costo lineal por km. En trayectos cortos
        # (el caso tipico de una moto haciendo ultima milla), el piso fijo
        # pesa proporcionalmente mas que en un trayecto largo -- por eso NO
        # es lineal puro, tiene un termino independiente de la distancia.
        return self.PISO_ARRANQUE_FRIO + kilometros * self.factor_ambiental
