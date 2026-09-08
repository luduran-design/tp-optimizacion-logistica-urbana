from modelado.transporte import Transporte


class Camion(Transporte):
    def calcular_impacto(self, kilometros, carga_kg):
        # Un camion cargado contamina mas que uno vacio: se agrega un factor
        # multiplicativo que crece segun que porcentaje de su capacidad va
        # transportando.
        factor_carga = 1 + (carga_kg / self.capacidad_peso)
        return kilometros * self.factor_ambiental * factor_carga
