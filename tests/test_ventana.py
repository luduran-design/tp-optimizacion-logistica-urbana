"""Tests de Ventana (reglas 2 y 6): tipos, limites y comportamiento horario."""

import pytest

from modelado import Ventana, DatosInvalidos
from tests.helpers import _hora, _ventana


class TestValidacionVentana:
    def test_ventana_valida_construye(self):
        v = Ventana(_hora(10), _hora(20))
        assert v.inicio == _hora(10)
        assert v.fin == _hora(20)

    def test_inicio_igual_a_fin_es_valida(self):
        # Regla 2: inicio anterior O IGUAL al fin. Un solo instante es valido.
        v = Ventana(_hora(10), _hora(10))
        assert v.inicio == v.fin

    def test_inicio_mayor_a_fin_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="posterior"):
            Ventana(_hora(20), _hora(10))

    def test_numeros_en_vez_de_datetime_lanzan_error(self):
        # Convencion de tiempos: los limites son datetime, no numeros.
        with pytest.raises(DatosInvalidos, match="datetime"):
            Ventana(10, 20)

    def test_inicio_y_fin_son_de_solo_lectura(self):
        v = _ventana(10, 20)
        with pytest.raises(AttributeError):
            v.inicio = _hora(9)
        with pytest.raises(AttributeError):
            v.fin = _hora(21)


class TestLlegaTarde:
    """llega_tarde(instante): True si el instante paso el fin de la ventana."""

    def test_llegada_antes_del_fin_no_es_tarde(self):
        assert _ventana(10, 20).llega_tarde(_hora(15)) is False

    def test_llegada_exactamente_al_fin_no_es_tarde(self):
        # Regla 6: llegar exactamente al fin es valido (fin inclusivo).
        assert _ventana(10, 20).llega_tarde(_hora(20)) is False

    def test_llegada_un_minuto_despues_del_fin_es_tarde(self):
        assert _ventana(10, 20).llega_tarde(_hora(20, 1)) is True

    def test_llegada_antes_del_inicio_no_es_tarde(self):
        # Llegar temprano no es "tarde": es esperar.
        assert _ventana(10, 20).llega_tarde(_hora(5)) is False


class TestInicioDeServicio:
    """inicio_de_servicio(llegada): cuando arranca el servicio.
    Si llegaste antes de que se abra la ventana, esperas hasta el inicio.
    Si ya se abrio, arrancas al toque (regla 6)."""

    def test_llegada_antes_del_inicio_espera_hasta_el_inicio(self):
        assert _ventana(10, 20).inicio_de_servicio(_hora(5)) == _hora(10)

    def test_llegada_dentro_de_ventana_arranca_al_toque(self):
        assert _ventana(10, 20).inicio_de_servicio(_hora(15)) == _hora(15)

    def test_llegada_justo_al_inicio_arranca_al_toque(self):
        assert _ventana(10, 20).inicio_de_servicio(_hora(10)) == _hora(10)

    def test_inicio_de_servicio_no_modifica_la_ventana(self):
        v = _ventana(10, 20)
        v.inicio_de_servicio(_hora(5))
        assert v.inicio == _hora(10)
        assert v.fin == _hora(20)