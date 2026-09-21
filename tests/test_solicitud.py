"""Tests de Solicitud: comportamiento, validaciones, delegacion a Ventana, inmutabilidad."""

import pytest

from modelado import Solicitud, Ubicacion, Ventana, Articulo, DatosInvalidos
from tests.helpers import _articulos_basicos, _solicitud_basica


class TestSolicitud:
    def test_peso_total_suma_articulos(self):
        s = _solicitud_basica()
        assert s.peso_total() == 7.0

    def test_volumen_total_suma_articulos(self):
        s = _solicitud_basica()
        assert s.volumen_total() == 3.5

    def test_asignacion_arranca_en_false(self):
        assert _solicitud_basica().esta_asignada() is False

    def test_marcar_y_desmarcar_asignada(self):
        s = _solicitud_basica()
        s.marcar_como_asignada()
        assert s.esta_asignada() is True
        s.desmarcar_como_asignada()
        assert s.esta_asignada() is False


class TestValidacionSolicitud:
    def _destino(self):
        return Ubicacion("U1", "Palermo", "")

    def test_id_vacio_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="id"):
            Solicitud("", self._destino(), Ventana(0, 100), _articulos_basicos())

    def test_destino_none_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="destino"):
            Solicitud("S1", None, Ventana(0, 100), _articulos_basicos())

    def test_ventana_none_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="ventana"):
            Solicitud("S1", self._destino(), None, _articulos_basicos())

    def test_articulos_vacio_lanza_error(self):
        # Regla: una solicitud tiene que llevar al menos un articulo.
        with pytest.raises(DatosInvalidos, match="articulo"):
            Solicitud("S1", self._destino(), Ventana(0, 100), [])


class TestDelegacionAVentana:
    """Solicitud no reimplementa la logica horaria: delega en su Ventana.
    Verificamos que los resultados coinciden con los de la ventana subyacente."""

    def _solicitud_con_ventana(self, inicio, fin):
        destino = Ubicacion("U1", "Palermo", "")
        return Solicitud("S1", destino, Ventana(inicio, fin), _articulos_basicos())

    def test_llega_tarde_delega_a_ventana(self):
        s = self._solicitud_con_ventana(10, 20)
        # Delegacion pura: el resultado tiene que coincidir con Ventana.llega_tarde.
        assert s.llega_tarde(25) == s.ventana.llega_tarde(25)
        assert s.llega_tarde(15) == s.ventana.llega_tarde(15)

    def test_llega_tarde_con_instante_dentro_devuelve_false(self):
        s = self._solicitud_con_ventana(10, 20)
        assert s.llega_tarde(15) is False

    def test_llega_tarde_con_instante_pasado_devuelve_true(self):
        s = self._solicitud_con_ventana(10, 20)
        assert s.llega_tarde(25) is True

    def test_espera_desde_delega_a_ventana(self):
        s = self._solicitud_con_ventana(10, 20)
        assert s.espera_desde(5) == s.ventana.inicio_de_servicio(5)
        assert s.espera_desde(15) == s.ventana.inicio_de_servicio(15)

    def test_espera_desde_temprano_espera_al_inicio(self):
        s = self._solicitud_con_ventana(10, 20)
        assert s.espera_desde(5) == 10

    def test_espera_desde_dentro_arranca_al_toque(self):
        s = self._solicitud_con_ventana(10, 20)
        assert s.espera_desde(15) == 15


class TestInmutabilidadSolicitud:
    """id, destino, ventana y articulos son inmutables desde afuera. La lista
    de articulos se devuelve como copia (regla 2)."""

    def test_no_se_puede_reasignar_id(self):
        s = _solicitud_basica()
        with pytest.raises(AttributeError):
            s.id = "S99"

    def test_no_se_puede_reasignar_destino(self):
        s = _solicitud_basica()
        with pytest.raises(AttributeError):
            s.destino = Ubicacion("U99", "otro", "")

    def test_no_se_puede_reasignar_ventana(self):
        s = _solicitud_basica()
        with pytest.raises(AttributeError):
            s.ventana = Ventana(0, 10)

    def test_no_se_puede_reasignar_articulos(self):
        s = _solicitud_basica()
        with pytest.raises(AttributeError):
            s.articulos = []

    def test_mutar_articulos_devueltos_no_afecta_la_solicitud(self):
        """El ataque literal del issue: intentar sumar carga a una solicitud
        ya construida mutando la lista devuelta por la property."""
        s = _solicitud_basica()
        peso_original = s.peso_total()
        volumen_original = s.volumen_total()
        # La lista devuelta es copia: mutarla no cambia el interior.
        s.articulos.append(Articulo("A99", "pesado", 5000, 50))
        assert s.peso_total() == peso_original
        assert s.volumen_total() == volumen_original

    def test_mutar_articulos_originales_no_afecta_la_solicitud(self):
        """Copia defensiva de entrada: si el que construyo la solicitud despues
        muta la lista original, la solicitud no cambia."""
        destino = Ubicacion("U1", "Palermo", "")
        lista_original = _articulos_basicos()
        s = Solicitud("S1", destino, Ventana(0, 100), lista_original)
        peso_antes = s.peso_total()
        lista_original.append(Articulo("A99", "pesado", 5000, 50))
        assert s.peso_total() == peso_antes
