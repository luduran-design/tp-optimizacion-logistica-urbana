"""Tests de Parada: constructor, maquina de estados, datos de cierre, inmutabilidad."""

import pytest

from modelado import Parada, ResultadoParada, TransicionIlegal, Incidente, TipoIncidente
from tests.helpers import _solicitud_basica


class TestConstruccionParada:
    def test_arranca_en_pendiente(self):
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

    def test_arranca_sin_datos_de_cierre(self):
        # Los datos de entrega y del incidente se completan al cerrar la parada.
        p = Parada(1, _solicitud_basica(), 10)
        assert p.receptor is None
        assert p.fecha_hora_real is None
        assert p.incidente is None


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
        p = Parada(1, _solicitud_basica(), 10)
        p.marcar_fallida(None)
        with pytest.raises(TransicionIlegal):
            p.entregar("Juan", 20)

    def test_marcar_fallida_despues_de_entregada_lanza_error(self):
        p = Parada(1, _solicitud_basica(), 10)
        p.entregar("Juan", 20)
        with pytest.raises(TransicionIlegal):
            p.marcar_fallida(None)


class TestDatosDeCierre:
    """Al cerrar una parada, los datos que le pasamos quedan guardados: Parada
    es el registro de que paso."""

    def test_entregar_guarda_receptor_y_fecha(self):
        p = Parada(1, _solicitud_basica(), 10)
        p.entregar(receptor="Juan", fecha_hora=20)
        assert p.receptor == "Juan"
        assert p.fecha_hora_real == 20

    def test_marcar_fallida_guarda_incidente(self):
        p = Parada(1, _solicitud_basica(), 10)
        i = Incidente("I1", TipoIncidente.RETRASO, 15, "trafico", None)
        p.marcar_fallida(i)
        assert p.incidente is i


class TestActualizarOrden:
    """actualizar_orden es la unica via legitima para cambiar la posicion de una
    parada dentro del itinerario. Lo usa Itinerario cuando reordena o quita."""

    def test_actualizar_orden_cambia_la_posicion(self):
        p = Parada(1, _solicitud_basica(), 10)
        p.actualizar_orden(5)
        assert p.orden == 5


class TestInmutabilidadParada:
    """El estado de una parada (resultado, receptor, fecha_hora_real, incidente,
    solicitud, llegada_prevista) es privado: solo se puede tocar via entregar()
    o marcar_fallida(). El orden solo via actualizar_orden()."""

    def test_no_se_puede_setear_resultado_desde_afuera(self):
        # El ataque literal del issue: saltarse registrar_entrega() escribiendo
        # el resultado directo.
        p = Parada(1, _solicitud_basica(), 10)
        with pytest.raises(AttributeError):
            p.resultado = ResultadoParada.ENTREGADA

    def test_no_se_puede_setear_receptor_desde_afuera(self):
        p = Parada(1, _solicitud_basica(), 10)
        with pytest.raises(AttributeError):
            p.receptor = "Juan"

    def test_no_se_puede_setear_fecha_hora_real_desde_afuera(self):
        p = Parada(1, _solicitud_basica(), 10)
        with pytest.raises(AttributeError):
            p.fecha_hora_real = 20

    def test_no_se_puede_setear_incidente_desde_afuera(self):
        p = Parada(1, _solicitud_basica(), 10)
        with pytest.raises(AttributeError):
            p.incidente = None

    def test_no_se_puede_reasignar_solicitud(self):
        p = Parada(1, _solicitud_basica(), 10)
        with pytest.raises(AttributeError):
            p.solicitud = _solicitud_basica()

    def test_no_se_puede_reasignar_orden_por_asignacion(self):
        # El orden se cambia SOLO via actualizar_orden(), no con `p.orden = x`.
        p = Parada(1, _solicitud_basica(), 10)
        with pytest.raises(AttributeError):
            p.orden = 5

    def test_no_se_puede_reasignar_llegada_prevista(self):
        p = Parada(1, _solicitud_basica(), 10)
        with pytest.raises(AttributeError):
            p.llegada_prevista = 999
