"""Tests de la jerarquia de Transporte: polimorfismo real y validaciones."""

import pytest

from modelado import Furgoneta, DatosInvalidos
from tests.helpers import _make_transportes


class TestPolimorfismoImpacto:
    """La prueba clave: una unica llamada polimorfica t.calcular_impacto(km, carga)
    debe devolver valores DISTINTOS segun el subtipo, sin que el que llama
    tenga que preguntar de que tipo es t."""

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


class TestValidacionTransporte:
    """Se prueba a traves de Furgoneta porque Transporte es abstracta."""

    def test_transporte_valido_construye(self):
        # Sanity: los defaults del helper son validos.
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
        # Cero es valido (podria ser un transporte gratis en pruebas).
        f = Furgoneta("F1", 1000, 5.0, 60, 0, 50, 0.27)
        assert f.costo_por_km == 0

    def test_costo_por_parada_negativo_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="costo"):
            Furgoneta("F1", 1000, 5.0, 60, 200, -50, 0.27)

    def test_factor_ambiental_negativo_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="factor"):
            Furgoneta("F1", 1000, 5.0, 60, 200, 50, -0.1)

    def test_factor_ambiental_cero_es_valido(self):
        # Un vehiculo electrico ideal podria tener factor cero.
        f = Furgoneta("F1", 1000, 5.0, 60, 200, 50, 0)
        assert f.factor_ambiental == 0
