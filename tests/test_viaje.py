"""Tests de Viaje: enum de estado, maquina de estados, composicion con Itinerario."""

import pytest

from modelado import EstadoViaje, TransicionIlegal, Itinerario
from tests.helpers import _make_viaje_planificado


class TestEnumEstadoViaje:
    def test_estado_no_se_puede_asignar_con_string(self):
        # Es un Enum: aunque alguien haga viaje._estado = "Planificado"
        # (typo silencioso del ejemplo del ayudante), las comparaciones
        # con EstadoViaje.PLANIFICADO daran False y la maquina de estados
        # se rompera. Con Enum el tipeo esta forzado desde el vamos.
        v = _make_viaje_planificado()
        assert v.estado == EstadoViaje.PLANIFICADO
        # Comparar con string SIEMPRE es falso (no hay coincidencia silenciosa).
        assert v.estado != "PLANIFICADO"


class TestEstadoViaje_Maquina:
    def test_estado_inicial_es_planificado(self):
        assert _make_viaje_planificado().estado == EstadoViaje.PLANIFICADO

    def test_iniciar_pasa_a_en_curso(self):
        v = _make_viaje_planificado()
        v.iniciar()
        assert v.estado == EstadoViaje.EN_CURSO

    def test_iniciar_dos_veces_lanza_error(self):
        v = _make_viaje_planificado()
        v.iniciar()
        with pytest.raises(TransicionIlegal):
            v.iniciar()

    def test_finalizar_desde_planificado_lanza_error(self):
        # No se puede saltar de PLANIFICADO directo a FINALIZADO.
        with pytest.raises(TransicionIlegal):
            _make_viaje_planificado().finalizar()

    def test_ciclo_completo_planificado_encurso_finalizado(self):
        v = _make_viaje_planificado()
        v.iniciar()
        v.finalizar()
        assert v.estado == EstadoViaje.FINALIZADO

    def test_finalizar_dos_veces_lanza_error(self):
        v = _make_viaje_planificado()
        v.iniciar()
        v.finalizar()
        with pytest.raises(TransicionIlegal):
            v.finalizar()


class TestComposicionViajeItinerario:
    def test_viaje_expone_itinerario(self):
        v = _make_viaje_planificado()
        assert isinstance(v.itinerario, Itinerario)

    def test_paradas_arranca_vacio(self):
        assert _make_viaje_planificado().paradas == []

    def test_paradas_devuelve_copia_defensiva(self):
        v = _make_viaje_planificado()
        v.paradas.append("basura externa")
        assert v.paradas == []

    def test_comprobantes_devuelve_copia_defensiva(self):
        v = _make_viaje_planificado()
        v.comprobantes.append("basura externa")
        assert v.comprobantes == []

    def test_incidentes_devuelve_copia_defensiva(self):
        v = _make_viaje_planificado()
        v.incidentes.append("basura externa")
        assert v.incidentes == []
