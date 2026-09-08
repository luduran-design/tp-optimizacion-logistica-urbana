"""Tests de Empresa: colecciones, factory de Viaje, filtro de pendientes."""

from modelado import (
    Empresa, Deposito, MatrizDistancias, Furgoneta, Viaje, EstadoViaje,
)
from tests.helpers import _solicitud_basica


class TestEmpresa:
    def _empresa(self):
        d = Deposito("D1", "Central", "")
        return Empresa(d, MatrizDistancias([d]))

    def test_flota_arranca_vacia(self):
        assert self._empresa().flota == []

    def test_registrar_transporte_lo_agrega_a_flota(self):
        e = self._empresa()
        t = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0.27)
        e.registrar_transporte(t)
        assert t in e.flota

    def test_flota_devuelve_copia_defensiva(self):
        e = self._empresa()
        e.flota.append("basura")
        assert e.flota == []

    def test_crear_viaje_devuelve_viaje_planificado(self):
        e = self._empresa()
        t = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0.27)
        v = e.crear_viaje("V1", "2026-09-07", t, 8)
        assert isinstance(v, Viaje)
        assert v.estado == EstadoViaje.PLANIFICADO

    def test_crear_viaje_lo_guarda_en_viajes(self):
        e = self._empresa()
        t = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0.27)
        v = e.crear_viaje("V1", "2026-09-07", t, 8)
        assert v in e.viajes

    def test_solicitudes_pendientes_filtra_asignadas(self):
        e = self._empresa()
        s1 = _solicitud_basica("S1")
        s2 = _solicitud_basica("S2")
        s2.marcar_como_asignada()
        e.registrar_solicitud(s1)
        e.registrar_solicitud(s2)
        pendientes = e.solicitudes_pendientes()
        assert s1 in pendientes
        assert s2 not in pendientes
