"""Tests de Ubicacion (identidad, hash, y validaciones de constructor)."""

import pytest

from modelado import Ubicacion, DatosInvalidos


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


class TestValidacionUbicacion:
    def test_id_vacio_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="id"):
            Ubicacion("", "Palermo", "")

    def test_nombre_vacio_lanza_error(self):
        with pytest.raises(DatosInvalidos, match="nombre"):
            Ubicacion("U1", "", "")

    def test_descripcion_vacia_es_valida(self):
        # La descripcion SI puede quedar vacia, no lanza error.
        u = Ubicacion("U1", "Palermo", "")
        assert u.descripcion == ""
