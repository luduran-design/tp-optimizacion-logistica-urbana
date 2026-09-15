"""Tests de validaciones de constructor de Ventana + comportamiento horario."""

import pytest

from modelado import Ventana, DatosInvalidos


class TestValidacionVentana:
    def test_ventana_valida_construye(self):
        v = Ventana(10, 20)
        assert v.inicio == 10 and v.fin == 20

    def test_inicio_igual_a_fin_lanza_error(self):
        # Una ventana de duracion cero no tiene sentido.
        with pytest.raises(DatosInvalidos):
            Ventana(10, 10)

    def test_inicio_mayor_a_fin_lanza_error(self):
        with pytest.raises(DatosInvalidos):
            Ventana(20, 10)


class TestLlegaTarde:
    """llega_tarde(instante): True si el instante paso el fin de la ventana."""

    def test_llegada_antes_del_fin_no_es_tarde(self):
        v = Ventana(10, 20)
        assert v.llega_tarde(15) is False

    def test_llegada_al_fin_no_es_tarde(self):
        # El fin es inclusivo: instante == fin NO es tarde.
        v = Ventana(10, 20)
        assert v.llega_tarde(20) is False

    def test_llegada_despues_del_fin_es_tarde(self):
        v = Ventana(10, 20)
        assert v.llega_tarde(21) is True

    def test_llegada_antes_del_inicio_no_es_tarde(self):
        # Llegar temprano no es "tarde": es esperar.
        v = Ventana(10, 20)
        assert v.llega_tarde(5) is False


class TestInicioDeServicio:
    """inicio_de_servicio(llegada): cuando arranca el servicio.
    Si llegaste antes de que se abra la ventana, esperas hasta el inicio.
    Si ya se abrio, arrancas al toque."""

    def test_llegada_antes_del_inicio_espera(self):
        # Llego a las 5, la ventana abre a las 10 -> arranca a las 10.
        v = Ventana(10, 20)
        assert v.inicio_de_servicio(5) == 10

    def test_llegada_dentro_de_ventana_arranca_al_toque(self):
        # Llego a las 15, ventana abierta -> arranca a las 15.
        v = Ventana(10, 20)
        assert v.inicio_de_servicio(15) == 15

    def test_llegada_justo_al_inicio_arranca_al_toque(self):
        v = Ventana(10, 20)
        assert v.inicio_de_servicio(10) == 10
