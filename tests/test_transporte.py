"""Tests de la jerarquia de Transporte: polimorfismo, validaciones, tiempo, costo."""

import pytest

from modelado import Furgoneta, DatosInvalidos
from tests.helpers import _make_transportes


class TestPolimorfismoImpacto:
    """La prueba clave: una unica llamada polimorfica t.calcular_impacto(km, carga)
    debe devolver valores DISTINTOS segun el subtipo, sin que el que llama
    tenga que preguntar de que tipo es t."""

    def test_camion_con_carga_supera_a_furgoneta(self):
        _, f, c = _make_transportes()
        km, carga = 45, 1000
        assert c.calcular_impacto(km, carga) > f.calcular_impacto(km, carga)

    def test_moto_incluye_piso_de_arranque(self):
        m, f, _ = _make_transportes()
        assert m.calcular_impacto(45, 0) > f.calcular_impacto(45, 0)

    def test_camion_vacio_coincide_con_furgoneta(self):
        _, f, c = _make_transportes()
        assert c.calcular_impacto(45, 0) == pytest.approx(f.calcular_impacto(45, 0))

    def test_furgoneta_lineal_puro(self):
        # Ejemplo de aceptacion del README: 45 km, factor 0.27 -> 12.15
        _, f, _ = _make_transportes()
        assert f.calcular_impacto(45, 500) == pytest.approx(12.15)

    def test_llamada_polimorfica_uniforme(self):
        for t in _make_transportes():
            resultado = t.calcular_impacto(45, 500)
            assert isinstance(resultado, float)

    def test_admite_carga_respeta_capacidad(self):
        _, f, _ = _make_transportes()
        assert f.admite_carga(500, 3.0) is True
        assert f.admite_carga(2000, 3.0) is False  # supera peso
        assert f.admite_carga(500, 10.0) is False  # supera volumen


class TestTiempoDeTramo:
    """tiempo_de_tramo(km) = km / velocidad_media. Es comun a todos los transportes."""

    def test_tiempo_proporcional_a_distancia(self):
        _, f, _ = _make_transportes()  # velocidad_media = 60
        # 60 km / 60 km/h = 1 hora
        assert f.tiempo_de_tramo(60) == pytest.approx(1.0)

    def test_tiempo_cero_para_distancia_cero(self):
        _, f, _ = _make_transportes()
        assert f.tiempo_de_tramo(0) == 0

    def test_tiempo_se_calcula_igual_en_todos_los_subtipos(self):
        # No es abstracto: la formula es la misma para moto, furgoneta y camion.
        m, f, c = _make_transportes()  # Todos tienen velocidad distinta
        assert m.tiempo_de_tramo(40) == pytest.approx(1.0)  # 40 km / 40 km/h
        assert f.tiempo_de_tramo(60) == pytest.approx(1.0)  # 60 km / 60 km/h
        assert c.tiempo_de_tramo(50) == pytest.approx(1.0)  # 50 km / 50 km/h


class TestCalcularCosto:
    """calcular_costo(km, paradas) = km * costo_por_km + paradas * costo_por_parada."""

    def test_costo_es_suma_de_km_mas_paradas(self):
        _, f, _ = _make_transportes()  # costo_por_km=200, costo_por_parada=50
        # 10 km * 200 + 3 paradas * 50 = 2000 + 150 = 2150
        assert f.calcular_costo(10, 3) == pytest.approx(2150.0)

    def test_costo_sin_paradas_es_solo_kilometros(self):
        _, f, _ = _make_transportes()
        # 5 km * 200 = 1000
        assert f.calcular_costo(5, 0) == pytest.approx(1000.0)

    def test_costo_cero_km_cero_paradas_es_cero(self):
        _, f, _ = _make_transportes()
        assert f.calcular_costo(0, 0) == 0

    def test_costo_varia_por_transporte(self):
        # Cada subtipo tiene sus propios costos, la formula usa los del propio objeto.
        m, f, c = _make_transportes()
        # moto: 100*10 + 50*2 = 1100; furgoneta: 200*10 + 50*2 = 2100; camion: 500*10 + 100*2 = 5200
        assert m.calcular_costo(10, 2) == pytest.approx(1100.0)
        assert f.calcular_costo(10, 2) == pytest.approx(2100.0)
        assert c.calcular_costo(10, 2) == pytest.approx(5200.0)


class TestValidacionTransporte:
    """Se prueba a traves de Furgoneta porque Transporte es abstracta."""

    def test_transporte_valido_construye(self):
        _, f, _ = _make_transportes()
        assert f.id == "F1"

    def test_id_vacio_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="id"):
            Furgoneta("", 1000, 5.0, 60, 200, 50, 0.27)

    def test_capacidad_peso_cero_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="peso"):
            Furgoneta("F1", 0, 5.0, 60, 200, 50, 0.27)

    def test_capacidad_peso_negativa_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="peso"):
            Furgoneta("F1", -100, 5.0, 60, 200, 50, 0.27)

    def test_capacidad_volumen_cero_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="volumen"):
            Furgoneta("F1", 1000, 0, 60, 200, 50, 0.27)

    def test_velocidad_media_cero_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="velocidad"):
            Furgoneta("F1", 1000, 5.0, 0, 200, 50, 0.27)

    def test_costo_por_km_negativo_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="costo"):
            Furgoneta("F1", 1000, 5.0, 60, -1, 50, 0.27)

    def test_costo_por_km_cero_es_valido(self):
        f = Furgoneta("F1", 1000, 5.0, 60, 0, 50, 0.27)
        assert f.costo_por_km == 0

    def test_costo_por_parada_negativo_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="costo"):
            Furgoneta("F1", 1000, 5.0, 60, 200, -50, 0.27)

    def test_factor_ambiental_negativo_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="factor"):
            Furgoneta("F1", 1000, 5.0, 60, 200, 50, -0.1)

    def test_factor_ambiental_cero_es_valido(self):
        f = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0)
        assert f.factor_ambiental == 0
