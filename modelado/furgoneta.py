from modelado.transporte import Transporte


class Furgoneta(Transporte):
    def calcular_impacto(self, kilometros, carga_kg):
        # Caso base, lineal. Con los datos del ejemplo de aceptacion del
        # enunciado (45 km, factor 0.27) da 12.15 kg CO2 -- el numero exacto
        # que trae el README, asi que sirve para validar la formula con un test.
        return kilometros * self.factor_ambiental
