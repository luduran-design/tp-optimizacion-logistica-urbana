import pytest

from Modelado import (
    Ubicacion, Deposito, Articulo, Ventana, Solicitud,
    Motocicleta, Furgoneta, Camion,
    Parada, Incidente,
    MatrizDistancias, Itinerario, Viaje, Empresa,
    EstadoViaje, TipoIncidente, ResultadoParada,
    TransicionIlegalError,
)


# ============================================================
# Helpers de construccion (reutilizados por varios tests)
# ============================================================

def _articulos_basicos():
    return [Articulo("A1", "libro", 2.0, 0.5),
            Articulo("A2", "silla", 5.0, 3.0)]


def _solicitud_basica(id="S1"):
    destino = Ubicacion("U1", "Palermo", "")
    return Solicitud(id, destino, Ventana(0, 100), _articulos_basicos())


def _make_transportes(factor=0.27):
    # Mismo factor ambiental para todos: la diferencia SOLO viene
    # de la especializacion de cada subclase.
    m = Motocicleta("M1", 20, 0.5, 40, 100, 50, factor)
    f = Furgoneta("F1", 1000, 5.0, 60, 200, 50, factor)
    c = Camion("C1", 5000, 20.0, 50, 500, 100, factor)
    return m, f, c


def _make_viaje_planificado():
    deposito = Deposito("D1", "Central", "")
    matriz = MatrizDistancias([deposito])
    transporte = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0.27)
    return Viaje("V1", "2026-09-07", transporte, deposito, matriz, 8)


# ============================================================
# Ubicacion y Deposito
# ============================================================

class TestUbicacion:
    def test_igualdad_por_id(self):
        u1 = Ubicacion("U1", "Palermo", "")
        u2 = Ubicacion("U1", "OTRO NOMBRE", "OTRA DESC")
        assert u1 == u2

    def test_desigualdad_con_id_distinto(self):
        assert Ubicacion("U1", "a", "") != Ubicacion("U2", "a", "")

    def test_hash_consistente_con_eq(self):
        # Requisito para usar Ubicacion como clave en MatrizDistancias.
        u1 = Ubicacion("U1", "a", "")
        u2 = Ubicacion("U1", "b", "")
        assert hash(u1) == hash(u2)

    def test_no_es_deposito_por_default(self):
        assert Ubicacion("U1", "a", "").es_deposito() is False


class TestDeposito:
    def test_es_deposito_true(self):
        assert Deposito("D1", "Central", "").es_deposito() is True

    def test_deposito_es_una_ubicacion(self):
        # Herencia: un Deposito debe ser una Ubicacion.
        assert isinstance(Deposito("D1", "Central", ""), Ubicacion)


# ============================================================
# Solicitud
# ============================================================

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


# ============================================================
# Polimorfismo real (Issue #2 -- regla 9)
# ============================================================

class TestPolimorfismoImpacto:
    """
    La prueba clave: una unica llamada polimorfica t.calcular_impacto(km, carga)
    debe devolver valores DISTINTOS segun el subtipo, sin que el que llama
    tenga que preguntar de que tipo es t.
    """

    def test_camion_con_carga_supera_a_furgoneta(self):
        # El test que HOY fallaria con la firma vieja de Camion,
        # que colapsaba en el mismo numero que Furgoneta.
        _, f, c = _make_transportes()
        km, carga = 45, 1000
        assert c.calcular_impacto(km, carga) > f.calcular_impacto(km, carga)

    def test_moto_incluye_piso_de_arranque(self):
        m, f, _ = _make_transportes()
        assert m.calcular_impacto(45, 0) > f.calcular_impacto(45, 0)

    def test_camion_vacio_coincide_con_furgoneta(self):
        # Sanity check: sin carga, el factor colapsa a 1.
        _, f, c = _make_transportes()
        assert c.calcular_impacto(45, 0) == pytest.approx(f.calcular_impacto(45, 0))

    def test_furgoneta_lineal_puro(self):
        # Ejemplo de aceptacion del README: 45 km, factor 0.27 -> 12.15
        _, f, _ = _make_transportes()
        assert f.calcular_impacto(45, 500) == pytest.approx(12.15)

    def test_llamada_polimorfica_uniforme(self):
        # El codigo cliente no necesita saber el subtipo.
        for t in _make_transportes():
            resultado = t.calcular_impacto(45, 500)
            assert isinstance(resultado, float)

    def test_admite_carga_respeta_capacidad(self):
        _, f, _ = _make_transportes()
        assert f.admite_carga(500, 3.0) is True
        assert f.admite_carga(2000, 3.0) is False  # supera peso
        assert f.admite_carga(500, 10.0) is False  # supera volumen


# ============================================================
# Enums (Issue #1 -- reglas 11, 12)
# ============================================================

class TestEnumParada:
    def test_resultado_valido_construye(self):
        p = Parada(1, _solicitud_basica(), 10, ResultadoParada.ENTREGADA)
        assert p.resultado == ResultadoParada.ENTREGADA

    def test_resultado_string_libre_lanza_error(self):
        # Antes: aceptaba "CANCELADA" sin chistar. Ahora rechaza.
        with pytest.raises(ValueError, match="ResultadoParada"):
            Parada(1, _solicitud_basica(), 10, "CANCELADA")

    def test_resultado_none_lanza_error(self):
        with pytest.raises(ValueError, match="ResultadoParada"):
            Parada(1, _solicitud_basica(), 10, None)


class TestEnumIncidente:
    def test_tipo_valido_construye(self):
        i = Incidente("I1", TipoIncidente.DANIO, 10, "paquete roto", None)
        assert i.tipo == TipoIncidente.DANIO

    def test_tipo_string_libre_lanza_error(self):
        # El ejemplo textual del ayudante: "EL_PERRO_SE_COMIO_EL_PAQUETE"
        # ya no se puede construir.
        with pytest.raises(ValueError, match="TipoIncidente"):
            Incidente("I1", "EL_PERRO_SE_COMIO_EL_PAQUETE", 10, "x", None)

    def test_descripcion_vacia_lanza_error(self):
        # Regla 12 prohibe descripcion vacia.
        with pytest.raises(ValueError, match="descripcion"):
            Incidente("I1", TipoIncidente.DANIO, 10, "", None)


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


# ============================================================
# Maquina de estados del Viaje (regla 10)
# ============================================================

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
        with pytest.raises(TransicionIlegalError):
            v.iniciar()

    def test_finalizar_desde_planificado_lanza_error(self):
        # No se puede saltar de PLANIFICADO directo a FINALIZADO.
        with pytest.raises(TransicionIlegalError):
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
        with pytest.raises(TransicionIlegalError):
            v.finalizar()


# ============================================================
# Composicion Viaje -> Itinerario (Issue #3)
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
# Empresa (unificada a @property + factory)
# ============================================================

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
