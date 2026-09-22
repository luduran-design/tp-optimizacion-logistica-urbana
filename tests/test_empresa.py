"""Tests de Empresa: colecciones, factory de Viaje, filtro de pendientes."""

import pytest

from modelado import (
    Empresa, Deposito, MatrizDistancias, Furgoneta, Viaje, EstadoViaje,
    DatosInvalidos,
)
from tests.helpers import _solicitud_basica, _hora


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
        v = e.crear_viaje("V1", "2026-09-07", t, _hora(8))
        assert isinstance(v, Viaje)
        assert v.estado == EstadoViaje.PLANIFICADO

    def test_crear_viaje_lo_guarda_en_viajes(self):
        e = self._empresa()
        t = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0.27)
        v = e.crear_viaje("V1", "2026-09-07", t, _hora(8))
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

    # --- Regla 1: ids de viaje no vacios y unicos dentro de la empresa ---

    def test_crear_viaje_con_id_vacio_lanza_error(self):
        e = self._empresa()
        t = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0.27)
        with pytest.raises(DatosInvalidos, match="id"):
            e.crear_viaje("", "2026-09-07", t, _hora(8))
        assert e.viajes == []

    def test_crear_viaje_con_id_repetido_lanza_error(self):
        e = self._empresa()
        t = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0.27)
        e.crear_viaje("V1", "2026-09-07", t, _hora(8))
        with pytest.raises(DatosInvalidos, match="V1"):
            e.crear_viaje("V1", "2026-09-08", t, _hora(9))
        assert len(e.viajes) == 1

    def test_registrar_transporte_repetido_lanza_error(self):
        e = self._empresa()
        e.registrar_transporte(Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0.27))
        with pytest.raises(DatosInvalidos, match="F1"):
            e.registrar_transporte(Furgoneta("F1", 500, 2.0, 40, 100, 10, 0.3))
        assert len(e.flota) == 1