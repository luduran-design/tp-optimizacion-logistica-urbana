from modelado.ubicacion import Ubicacion


class Deposito(Ubicacion):
    def es_deposito(self) -> bool:
        return True
