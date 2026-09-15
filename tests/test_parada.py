"""Tests de Parada: constructor y maquina de estados (PENDIENTE -> ENTREGADA/FALLIDA)."""

import pytest

from modelado import Parada, ResultadoParada, TransicionIlegal
from tests.helpers import _solicitud_basica


class TestConstruccionParada:
    def test_arranca_en_pendiente(self):
        # Ya no se pasa el resultado por constructor: arranca en PENDIENTE.
        p = Parada(1, _solicitud_basica(), 10)
        assert p.resultado == ResultadoParada.PENDIENTE

    def test_esta_pendiente_true_al_arranque(self):
        p = Parada(1, _solicitud_basica(), 10)
        assert p.esta_pendiente() is True

    def test_guarda_atributos_basicos(self):
        s = _solicitud_basica()
        p = Parada(3, s, 15)
        assert p.orden == 3
        assert p.solicitud == s
        assert p.llegada_prevista == 15


class TestMaquinaEstadosParada:
    """Maquina de estados: PENDIENTE es el unico estado desde el que se
    puede salir. Una vez ENTREGADA o FALLIDA, no se puede volver atras."""

    def test_entregar_desde_pendiente_pasa_a_entregada(self):
        p = Parada(1, _solicitud_basica(), 10)
        p.entregar(receptor="Juan", fecha_hora=20)
        assert p.resultado == ResultadoParada.ENTREGADA
        assert p.esta_pendiente() is False

    def test_marcar_fallida_desde_pendiente_pasa_a_fallida(self):
        p = Parada(1, _solicitud_basica(), 10)
        p.marcar_fallida(incidente=None)
        assert p.resultado == ResultadoParada.FALLIDA
        assert p.esta_pendiente() is False

    def test_entregar_dos_veces_lanza_error(self):
        p = Parada(1, _solicitud_basica(), 10)
        p.entregar("Juan", 20)
        with pytest.raises(TransicionIlegal):
            p.entregar("Otro", 25)

    def test_marcar_fallida_dos_veces_lanza_error(self):
        p = Parada(1, _solicitud_basica(), 10)
        p.marcar_fallida(None)
        with pytest.raises(TransicionIlegal):
            p.marcar_fallida(None)

    def test_entregar_despues_de_fallida_lanza_error(self):
        # No se puede "revivir" una parada fallida entregandola.
        p = Parada(1, _solicitud_basica(), 10)
        p.marcar_fallida(None)
        with pytest.raises(TransicionIlegal):
            p.entregar("Juan", 20)

    def test_marcar_fallida_despues_de_entregada_lanza_error(self):
        # Simetrico al anterior: no se puede fallar algo ya entregado.
        p = Parada(1, _solicitud_basica(), 10)
        p.entregar("Juan", 20)
        with pytest.raises(TransicionIlegal):
            p.marcar_fallida(None)
