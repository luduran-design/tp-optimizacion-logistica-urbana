"""Tests de Viaje: enum, maquina de estados, composicion, ejecucion, resumen."""

import pytest

from modelado import (
    EstadoViaje, TransicionIlegal, Itinerario, DatosInvalidos,
    Deposito, Ubicacion, Solicitud, Articulo,
    MatrizDistancias, Furgoneta, Viaje,
    Incidente, TipoIncidente,
)
from tests.helpers import _make_viaje_planificado, _hora, _ventana_amplia


# ============================================================
# Helpers locales para armar viajes con solicitudes reales
# ============================================================

def _matriz_completa():
    """Deposito + 2 destinos con todos los tramos (ida y vuelta)."""
    d = Deposito("D1", "Central", "")
    u1 = Ubicacion("U1", "Palermo", "")
    u2 = Ubicacion("U2", "Belgrano", "")
    matriz = MatrizDistancias([d, u1, u2])
    for a, b, km in [(d, u1, 5), (u1, d, 5), (d, u2, 8), (u2, d, 8),
                     (u1, u2, 3), (u2, u1, 3)]:
        matriz.agregar_tramo(a, b, km)
    return d, u1, u2, matriz


def _solicitud(id, destino, peso=1.0):
    art = Articulo(f"A-{id}", "paquete", peso, 0.1)
    return Solicitud(id, destino, _ventana_amplia(), [art])


def _viaje_con_solicitudes(cantidad=2):
    """Devuelve (viaje, [solicitudes]) con las solicitudes ya agregadas."""
    d, u1, u2, matriz = _matriz_completa()
    transporte = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0.27)
    viaje = Viaje("V1", "2026-09-07", transporte, d, matriz, _hora(8))
    destinos = [u1, u2]
    solicitudes = []
    for i in range(cantidad):
        s = _solicitud(f"S{i+1}", destinos[i % 2], peso=2.0)
        viaje.agregar_solicitud(s)
        solicitudes.append(s)
    return viaje, solicitudes


def _viaje_finalizado():
    """Arma un viaje que ya paso por PLANIFICADO -> EN_CURSO -> FINALIZADO
    con una solicitud entregada, para usar en tests que necesitan estado FINALIZADO."""
    viaje, [s1] = _viaje_con_solicitudes(1)
    viaje.iniciar()
    viaje.registrar_entrega(s1, "Juan", _hora(9, 30))
    viaje.finalizar()
    return viaje


# ============================================================
# Enum de estado
# ============================================================

class TestEnumEstadoViaje:
    def test_estado_no_se_puede_asignar_con_string(self):
        v = _make_viaje_planificado()
        assert v.estado == EstadoViaje.PLANIFICADO
        assert v.estado != "PLANIFICADO"


# ============================================================
# Maquina de estados (transiciones directas)
# ============================================================

class TestEstadoViaje_Maquina:
    def test_estado_inicial_es_planificado(self):
        assert _make_viaje_planificado().estado == EstadoViaje.PLANIFICADO

    def test_iniciar_pasa_a_en_curso(self):
        viaje, _ = _viaje_con_solicitudes(1)
        viaje.iniciar()
        assert viaje.estado == EstadoViaje.EN_CURSO

    def test_iniciar_dos_veces_lanza_error(self):
        viaje, _ = _viaje_con_solicitudes(1)
        viaje.iniciar()
        with pytest.raises(TransicionIlegal):
            viaje.iniciar()

    def test_finalizar_desde_planificado_lanza_error(self):
        with pytest.raises(TransicionIlegal):
            _make_viaje_planificado().finalizar()

    def test_ciclo_completo_planificado_encurso_finalizado(self):
        viaje, [s1] = _viaje_con_solicitudes(1)
        viaje.iniciar()
        viaje.registrar_entrega(s1, "Juan", _hora(9, 30))
        viaje.finalizar()
        assert viaje.estado == EstadoViaje.FINALIZADO

    def test_finalizar_dos_veces_lanza_error(self):
        viaje = _viaje_finalizado()
        with pytest.raises(TransicionIlegal):
            viaje.finalizar()


# ============================================================
# Precondiciones de transicion (reglas 10 y 12)
# ============================================================

class TestPrecondicionesTransicion:
    def test_agregar_solicitud_en_en_curso_lanza_error(self):
        viaje, [s1] = _viaje_con_solicitudes(1)
        viaje.iniciar()
        _, _, u2, _ = _matriz_completa()
        s_nueva = _solicitud("S99", u2, peso=2.0)
        with pytest.raises(TransicionIlegal):
            viaje.agregar_solicitud(s_nueva)

    def test_agregar_solicitud_en_finalizado_lanza_error(self):
        viaje = _viaje_finalizado()
        _, u1, _, _ = _matriz_completa()
        s_nueva = _solicitud("S99", u1, peso=2.0)
        with pytest.raises(TransicionIlegal):
            viaje.agregar_solicitud(s_nueva)

    def test_iniciar_sin_paradas_lanza_error(self):
        v = _make_viaje_planificado()
        with pytest.raises(TransicionIlegal):
            v.iniciar()

    def test_finalizar_con_paradas_pendientes_lanza_error(self):
        viaje, _ = _viaje_con_solicitudes(2)
        viaje.iniciar()
        with pytest.raises(TransicionIlegal):
            viaje.finalizar()


# ============================================================
# Doble asignacion entre viajes (regla 5)
# ============================================================

class TestDobleAsignacionEntreViajes:
    def test_no_se_puede_agregar_misma_solicitud_a_dos_viajes(self):
        """Regla 5: una solicitud no puede pertenecer a dos viajes activos."""
        d, u1, _, matriz = _matriz_completa()
        f1 = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0.27)
        f2 = Furgoneta("F2", 1000, 5.0, 60, 200, 50, 0.27)
        v1 = Viaje("V1", "2026-09-07", f1, d, matriz, _hora(8))
        v2 = Viaje("V2", "2026-09-07", f2, d, matriz, _hora(8))

        s = _solicitud("S1", u1, peso=2.0)
        v1.agregar_solicitud(s)
        assert s.esta_asignada() is True

        with pytest.raises(DatosInvalidos):
            v2.agregar_solicitud(s)

        assert v2.paradas == []

    def test_no_se_puede_agregar_solicitud_ya_entregada_a_otro_viaje(self):
        """Regla 5: una solicitud entregada no puede volver a planificarse."""
        v1 = _viaje_finalizado()
        s_entregada = v1.paradas[0].solicitud
        assert s_entregada.esta_asignada() is True

        d, u1, _, matriz = _matriz_completa()
        f = Furgoneta("F2", 1000, 5.0, 60, 200, 50, 0.27)
        v2 = Viaje("V2", "2026-09-07", f, d, matriz, _hora(8))
        with pytest.raises(DatosInvalidos):
            v2.agregar_solicitud(s_entregada)
        assert v2.paradas == []


# ============================================================
# Orden de ejecucion de las paradas (regla 11)
# ============================================================

class TestOrdenDeEjecucion:
    """Regla 11: las paradas terminan en el orden planificado. Solo se puede
    entregar/fallar la parada actual (la primera pendiente)."""

    def test_no_se_puede_entregar_fuera_de_orden(self):
        viaje, [s1, s2] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        # S2 es la segunda: no se puede tocar mientras S1 siga pendiente.
        with pytest.raises(TransicionIlegal):
            viaje.registrar_entrega(s2, "Juan", _hora(9, 30))
        # Nada cambio: S1 sigue siendo la parada actual y no hay comprobantes.
        assert viaje.parada_actual().solicitud == s1
        assert viaje.comprobantes == []

    def test_no_se_puede_fallar_fuera_de_orden(self):
        viaje, [s1, s2] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        incidente = Incidente("I1", TipoIncidente.AUSENTE, _hora(9, 30), "nadie", s2)
        with pytest.raises(TransicionIlegal):
            viaje.registrar_fallo(s2, incidente)
        assert viaje.parada_actual().solicitud == s1
        assert viaje.incidentes == []

    def test_entregar_en_orden_avanza_a_la_siguiente(self):
        viaje, [s1, s2] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        viaje.registrar_entrega(s1, "Juan", _hora(9, 30))
        # Ahora S2 es la actual y se puede entregar.
        viaje.registrar_entrega(s2, "Ana", _hora(10))
        assert viaje.esta_completo() is True

    def test_entregar_con_receptor_vacio_lanza_error_y_no_cambia_estado(self):
        """Comprobante valida receptor no vacio (regla 11). Como se fabrica
        antes de cerrar la parada, si falla no queda estado sucio."""
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        with pytest.raises(DatosInvalidos):
            viaje.registrar_entrega(s1, "", _hora(9, 30))
        # Atomicidad: la parada NO debe haber quedado entregada,
        # y no debe haber comprobante nuevo.
        assert viaje.parada_actual().solicitud == s1
        assert viaje.comprobantes == []

    def test_entregar_una_solicitud_ajena_al_viaje_lanza_error(self):
        # Solicitud que no esta en el viaje: la parada actual es otra, asi
        # que _parada_para tira TransicionIlegal.
        viaje, _ = _viaje_con_solicitudes(2)
        viaje.iniciar()
        s_ajena = _solicitud("S99", Ubicacion("U99", "x", ""))
        with pytest.raises(TransicionIlegal):
            viaje.registrar_entrega(s_ajena, "Juan", _hora(9, 30))

    def test_fallar_una_solicitud_ajena_al_viaje_lanza_error(self):
        viaje, _ = _viaje_con_solicitudes(2)
        viaje.iniciar()
        s_ajena = _solicitud("S99", Ubicacion("U99", "x", ""))
        incidente = Incidente("I1", TipoIncidente.AUSENTE, _hora(9, 30), "nadie", s_ajena)
        with pytest.raises(TransicionIlegal):
            viaje.registrar_fallo(s_ajena, incidente)


# ============================================================
# Composicion con Itinerario
# ============================================================

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


# ============================================================
# Quitar solicitud (delegacion + guardia de estado)
# ============================================================

class TestQuitarSolicitud:
    def test_quitar_en_planificado_funciona(self):
        viaje, [s1, s2] = _viaje_con_solicitudes(2)
        viaje.quitar_solicitud(s1)
        assert s1 not in [p.solicitud for p in viaje.paradas]

    def test_quitar_en_en_curso_lanza_error(self):
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        with pytest.raises(TransicionIlegal):
            viaje.quitar_solicitud(s1)

    def test_quitar_en_finalizado_lanza_error(self):
        viaje = _viaje_finalizado()
        s_cualquiera = _solicitud("SX", Ubicacion("UX", "x", ""))
        with pytest.raises(TransicionIlegal):
            viaje.quitar_solicitud(s_cualquiera)


# ============================================================
# Reordenar (delegacion + guardia de estado)
# ============================================================

class TestReordenarViaje:
    def test_reordenar_en_planificado_funciona(self):
        viaje, [s1, s2] = _viaje_con_solicitudes(2)
        viaje.reordenar([s2, s1])
        assert [p.solicitud for p in viaje.paradas] == [s2, s1]

    def test_reordenar_en_en_curso_lanza_error(self):
        viaje, [s1, s2] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        with pytest.raises(TransicionIlegal):
            viaje.reordenar([s2, s1])

    def test_reordenar_en_finalizado_lanza_error(self):
        viaje = _viaje_finalizado()
        with pytest.raises(TransicionIlegal):
            viaje.reordenar([])


# ============================================================
# esta_completo
# ============================================================

class TestEstaCompleto:
    def test_viaje_vacio_esta_completo(self):
        # all([]) es True: sin paradas pendientes, esta "completo" trivialmente.
        assert _make_viaje_planificado().esta_completo() is True

    def test_viaje_con_paradas_pendientes_no_esta_completo(self):
        viaje, _ = _viaje_con_solicitudes(2)
        assert viaje.esta_completo() is False

    def test_viaje_con_todas_las_paradas_entregadas_esta_completo(self):
        viaje, [s1, s2] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        viaje.registrar_entrega(s1, "Juan", _hora(9, 30))
        viaje.registrar_entrega(s2, "Ana", _hora(10))
        assert viaje.esta_completo() is True

    def test_viaje_con_paradas_falladas_tambien_cuenta_como_completo(self):
        # Una parada fallida ya no esta pendiente, asi que el viaje esta completo.
        viaje, [s1, s2] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        viaje.registrar_entrega(s1, "Juan", _hora(9, 30))
        incidente = Incidente("I1", TipoIncidente.AUSENTE, _hora(10), "nadie", s2)
        viaje.registrar_fallo(s2, incidente)
        assert viaje.esta_completo() is True


# ============================================================
# parada_actual
# ============================================================

class TestParadaActual:
    def test_viaje_vacio_no_tiene_parada_actual(self):
        assert _make_viaje_planificado().parada_actual() is None

    def test_parada_actual_es_la_primera_pendiente(self):
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        actual = viaje.parada_actual()
        assert actual.solicitud == s1

    def test_parada_actual_avanza_despues_de_entregar(self):
        viaje, [s1, s2] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        viaje.registrar_entrega(s1, "Juan", _hora(9, 30))
        actual = viaje.parada_actual()
        assert actual.solicitud == s2

    def test_parada_actual_es_none_cuando_todo_esta_entregado(self):
        viaje, [s1, s2] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        viaje.registrar_entrega(s1, "Juan", _hora(9, 30))
        viaje.registrar_entrega(s2, "Ana", _hora(10))
        assert viaje.parada_actual() is None


# ============================================================
# recorrer (transiciones automaticas)
# ============================================================

class TestRecorrer:
    def test_recorrer_desde_planificado_pasa_a_en_curso(self):
        viaje, _ = _viaje_con_solicitudes(2)
        viaje.recorrer()
        assert viaje.estado == EstadoViaje.EN_CURSO

    def test_recorrer_desde_en_curso_completo_pasa_a_finalizado(self):
        viaje, [s1] = _viaje_con_solicitudes(1)
        viaje.iniciar()
        viaje.registrar_entrega(s1, "Juan", _hora(9, 30))
        viaje.recorrer()  # EN_CURSO + completo -> FINALIZADO
        assert viaje.estado == EstadoViaje.FINALIZADO

    def test_recorrer_desde_en_curso_no_completo_no_avanza(self):
        viaje, _ = _viaje_con_solicitudes(2)
        viaje.iniciar()
        viaje.recorrer()  # sigue habiendo paradas pendientes
        assert viaje.estado == EstadoViaje.EN_CURSO

    def test_recorrer_desde_finalizado_no_hace_nada(self):
        viaje = _viaje_finalizado()
        viaje.recorrer()  # no debe lanzar error ni cambiar estado
        assert viaje.estado == EstadoViaje.FINALIZADO


# ============================================================
# registrar_entrega
# ============================================================

class TestRegistrarEntrega:
    def test_registrar_entrega_marca_parada_como_entregada(self):
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        viaje.registrar_entrega(s1, "Juan", _hora(9, 30))
        parada = next(p for p in viaje.paradas if p.solicitud == s1)
        assert parada.esta_pendiente() is False

    def test_registrar_entrega_crea_un_comprobante(self):
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        viaje.registrar_entrega(s1, "Juan", _hora(9, 30))
        assert len(viaje.comprobantes) == 1
        assert viaje.comprobantes[0].receptor == "Juan"

    def test_registrar_entrega_guarda_datos_en_la_parada(self):
        # La parada ahora es un registro completo: guarda quien recibio y cuando.
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        viaje.registrar_entrega(s1, "Juan", _hora(9, 30))
        parada = next(p for p in viaje.paradas if p.solicitud == s1)
        assert parada.receptor == "Juan"
        assert parada.fecha_hora_real == _hora(9, 30)

    def test_registrar_entrega_en_planificado_lanza_error(self):
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        # sin iniciar: sigue en PLANIFICADO
        with pytest.raises(TransicionIlegal):
            viaje.registrar_entrega(s1, "Juan", _hora(9, 30))

    def test_registrar_entrega_en_finalizado_lanza_error(self):
        viaje = _viaje_finalizado()
        s = _solicitud("SX", Ubicacion("UX", "x", ""))
        with pytest.raises(TransicionIlegal):
            viaje.registrar_entrega(s, "Juan", _hora(9, 30))


# ============================================================
# registrar_fallo
# ============================================================

class TestRegistrarFallo:
    def _incidente(self, solicitud):
        return Incidente("I1", TipoIncidente.DANIO, _hora(9, 30), "paquete roto", solicitud)

    def test_registrar_fallo_marca_parada_como_fallida(self):
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        viaje.registrar_fallo(s1, self._incidente(s1))
        parada = next(p for p in viaje.paradas if p.solicitud == s1)
        assert parada.esta_pendiente() is False

    def test_registrar_fallo_agrega_incidente_a_la_lista(self):
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        i = self._incidente(s1)
        viaje.registrar_fallo(s1, i)
        assert i in viaje.incidentes

    def test_registrar_fallo_guarda_incidente_en_la_parada(self):
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        i = self._incidente(s1)
        viaje.registrar_fallo(s1, i)
        parada = next(p for p in viaje.paradas if p.solicitud == s1)
        assert parada.incidente is i

    def test_registrar_fallo_en_planificado_lanza_error(self):
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        with pytest.raises(TransicionIlegal):
            viaje.registrar_fallo(s1, self._incidente(s1))

    def test_registrar_fallo_en_finalizado_lanza_error(self):
        viaje = _viaje_finalizado()
        s = _solicitud("SX", Ubicacion("UX", "x", ""))
        with pytest.raises(TransicionIlegal):
            viaje.registrar_fallo(s, self._incidente(s))


# ============================================================
# registrar_incidente (directo, sin marcar parada)
# ============================================================

class TestRegistrarIncidente:
    def test_registrar_incidente_lo_agrega_a_la_lista(self):
        v = _make_viaje_planificado()
        i = Incidente("I1", TipoIncidente.RETRASO, _hora(8, 15), "trafico", v.itinerario.transporte)
        v.registrar_incidente(i)
        assert i in v.incidentes

    def test_registrar_incidente_sobre_solicitud_del_viaje(self):
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        i = Incidente("I1", TipoIncidente.RETRASO, _hora(8, 15), "demora en la entrega", s1)
        viaje.registrar_incidente(i)
        assert i in viaje.incidentes

    def test_registrar_incidente_sobre_solicitud_ajena_lanza_error(self):
        # Regla 12: el afectado debe ser una solicitud del viaje o su transporte.
        viaje, _ = _viaje_con_solicitudes(2)
        s_ajena = _solicitud("S99", Ubicacion("U99", "x", ""))
        i = Incidente("I1", TipoIncidente.RETRASO, _hora(8, 15), "demora", s_ajena)
        with pytest.raises(DatosInvalidos, match="no pertenece"):
            viaje.registrar_incidente(i)
        assert viaje.incidentes == []

    def test_registrar_incidente_sobre_otro_transporte_lanza_error(self):
        viaje, _ = _viaje_con_solicitudes(2)
        otro = Furgoneta("F99", 1000, 5.0, 60, 200, 50, 0.27)
        i = Incidente("I1", TipoIncidente.DANIO, _hora(8, 15), "choque", otro)
        with pytest.raises(DatosInvalidos, match="no es el de este viaje"):
            viaje.registrar_incidente(i)
        assert viaje.incidentes == []

    def test_registrar_algo_que_no_es_incidente_lanza_error(self):
        viaje, _ = _viaje_con_solicitudes(2)
        with pytest.raises(DatosInvalidos, match="Incidente"):
            viaje.registrar_incidente("se rompio algo")
        assert viaje.incidentes == []


class TestRegistrarFalloExigeIncidente:
    """Regla 11: una parada fallida exige al menos un incidente, vinculado a la
    entrega afectada. Si el incidente no sirve, la parada sigue pendiente."""

    def test_fallo_sin_incidente_lanza_error_y_parada_sigue_pendiente(self):
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        with pytest.raises(DatosInvalidos, match="Incidente"):
            viaje.registrar_fallo(s1, None)
        assert viaje.parada_actual().solicitud == s1
        assert viaje.incidentes == []

    def test_fallo_con_incidente_de_otra_solicitud_lanza_error(self):
        viaje, [s1, s2] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        i = Incidente("I1", TipoIncidente.AUSENTE, _hora(9, 30), "nadie", s2)
        with pytest.raises(DatosInvalidos, match="no a la solicitud"):
            viaje.registrar_fallo(s1, i)
        assert viaje.parada_actual().solicitud == s1
        assert viaje.incidentes == []

    def test_fallo_con_incidente_del_transporte_es_valido(self):
        # Un desperfecto del vehiculo tambien explica una entrega fallida.
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        viaje.iniciar()
        i = Incidente("I1", TipoIncidente.DANIO, _hora(9, 30), "pinchazo", viaje.itinerario.transporte)
        viaje.registrar_fallo(s1, i)
        assert viaje.parada_actual().solicitud != s1
        assert i in viaje.incidentes


# ============================================================
# resumen: foto de solo lectura
# ============================================================

class TestResumen:
    def test_resumen_devuelve_un_dict(self):
        v = _make_viaje_planificado()
        assert isinstance(v.resumen(), dict)

    def test_resumen_incluye_las_claves_esperadas(self):
        v = _make_viaje_planificado()
        r = v.resumen()
        claves = {"id", "fecha", "estado", "transporte", "deposito",
                  "cantidad_paradas", "distancia_km", "carga_peso",
                  "carga_volumen", "costo", "impacto_ambiental",
                  "hora_regreso", "es_factible", "entregas", "incidentes"}
        assert claves.issubset(r.keys())

    def test_resumen_refleja_el_estado_actual(self):
        viaje, _ = _viaje_con_solicitudes(1)
        assert viaje.resumen()["estado"] == "PLANIFICADO"
        viaje.iniciar()
        assert viaje.resumen()["estado"] == "EN_CURSO"

    def test_resumen_cuenta_paradas_y_entregas(self):
        viaje, [s1, _] = _viaje_con_solicitudes(2)
        assert viaje.resumen()["cantidad_paradas"] == 2
        assert viaje.resumen()["entregas"] == 0
        viaje.iniciar()
        viaje.registrar_entrega(s1, "Juan", _hora(9, 30))
        assert viaje.resumen()["entregas"] == 1

    def test_resumen_devuelve_un_dict_nuevo_en_cada_llamada(self):
        # Es una FOTO: mutar el dict devuelto no debe afectar futuras llamadas.
        v = _make_viaje_planificado()
        r1 = v.resumen()
        r1["estado"] = "ROTO"
        r2 = v.resumen()
        assert r2["estado"] == "PLANIFICADO"

# ============================================================
# Validacion del constructor (regla 1)
# ============================================================

class TestValidacionViaje:
    def _armar(self, id_viaje):
        d, _, _, matriz = _matriz_completa()
        t = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0.27)
        return Viaje(id_viaje, "2026-09-07", t, d, matriz, _hora(8))

    def test_id_valido_construye(self):
        assert self._armar("V1").id == "V1"

    def test_id_vacio_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="id"):
            self._armar("")

    def test_id_solo_espacios_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="id"):
            self._armar("   ")

    def test_id_none_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="id"):
            self._armar(None)