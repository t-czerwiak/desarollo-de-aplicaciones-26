"""
Tests unitarios para las clases del dominio (models.py).
Ejecutar con: python -m pytest tests_models.py -v
"""

import pytest
from models import Categoria, Ingrediente, Receta


# ---------------------------------------------------------------------------
# Categoria
# ---------------------------------------------------------------------------

class TestCategoria:
    def test_descripcion_completa_con_descripcion(self):
        cat = Categoria(1, "Pasta", "Platos a base de pasta")
        assert cat.descripcion_completa() == "Pasta: Platos a base de pasta"

    def test_descripcion_completa_sin_descripcion(self):
        cat = Categoria(1, "Pasta")
        assert cat.descripcion_completa() == "Pasta"

    def test_str(self):
        cat = Categoria(1, "Postres", "Dulces")
        assert str(cat) == "Postres"


# ---------------------------------------------------------------------------
# Ingrediente
# ---------------------------------------------------------------------------

class TestIngrediente:
    def setup_method(self):
        self.ing = Ingrediente(1, "Harina", "g", 0.002, 500.0)

    def test_costo_estimado_positivo(self):
        assert self.ing.costo_estimado(100) == 0.20

    def test_costo_estimado_cero(self):
        assert self.ing.costo_estimado(0) == 0.0

    def test_costo_estimado_negativo_lanza_error(self):
        with pytest.raises(ValueError):
            self.ing.costo_estimado(-10)

    def test_es_disponible_con_stock_suficiente(self):
        assert self.ing.es_disponible(100) is True

    def test_es_disponible_exacto(self):
        assert self.ing.es_disponible(500) is True

    def test_es_disponible_sin_stock_suficiente(self):
        assert self.ing.es_disponible(501) is False

    def test_es_disponible_sin_cantidad(self):
        assert self.ing.es_disponible() is True

    def test_str(self):
        assert str(self.ing) == "Harina (500.0 g)"


# ---------------------------------------------------------------------------
# Receta – es_compleja
# ---------------------------------------------------------------------------

class TestRecetaEsCompleja:
    def _receta(self, tiempo: int) -> Receta:
        return Receta(1, "Test", "", tiempo, "Media", 1)

    def test_no_compleja_por_debajo_limite(self):
        assert self._receta(59).es_compleja() is False

    def test_compleja_exactamente_en_limite(self):
        # 60 minutos exactos → compleja
        assert self._receta(60).es_compleja() is True

    def test_compleja_por_encima_limite(self):
        assert self._receta(90).es_compleja() is True

    def test_no_compleja_rapida(self):
        assert self._receta(15).es_compleja() is False


# ---------------------------------------------------------------------------
# Receta – tiempo_formateado
# ---------------------------------------------------------------------------

class TestRecetaTiempoFormateado:
    def _receta(self, tiempo: int) -> Receta:
        return Receta(1, "Test", "", tiempo, "Media", 1)

    def test_solo_minutos(self):
        assert self._receta(45).tiempo_formateado() == "45min"

    def test_solo_horas(self):
        # 120 min = 2h exactas
        assert self._receta(120).tiempo_formateado() == "2h"

    def test_horas_y_minutos(self):
        # 90 min = 1h 30min
        assert self._receta(90).tiempo_formateado() == "1h 30min"

    def test_cero_minutos(self):
        assert self._receta(0).tiempo_formateado() == "0min"


# ---------------------------------------------------------------------------
# Receta – pasos
# ---------------------------------------------------------------------------

class TestRecetaPasos:
    def _receta(self, preparacion: str) -> Receta:
        return Receta(1, "Test", "", 30, "Media", 1, "", preparacion)

    def test_varios_renglones(self):
        receta = self._receta("Hervir el agua.\nCocinar la pasta.\nServir.")
        assert receta.pasos() == ["Hervir el agua.", "Cocinar la pasta.", "Servir."]

    def test_un_solo_paso(self):
        assert self._receta("Mezclar todo.").pasos() == ["Mezclar todo."]

    def test_sin_preparacion(self):
        assert self._receta("").pasos() == []

    def test_receta_sin_el_campo_no_tiene_pasos(self):
        # El parámetro es opcional: una receta creada sin preparación no rompe.
        assert Receta(1, "Test", "", 30, "Media", 1).pasos() == []

    def test_descarta_renglones_vacios(self):
        receta = self._receta("Primero.\n\n\nSegundo.\n")
        assert receta.pasos() == ["Primero.", "Segundo."]

    def test_limpia_espacios_sobrantes(self):
        receta = self._receta("   Primero.   \n\t Segundo. ")
        assert receta.pasos() == ["Primero.", "Segundo."]

    def test_solo_espacios_no_es_paso(self):
        assert self._receta("   \n\t\n  ").pasos() == []


# ---------------------------------------------------------------------------
# Receta – variantes
# ---------------------------------------------------------------------------

class TestRecetaVariantes:
    def _receta(self, variaciones: str) -> Receta:
        return Receta(1, "Test", "", 30, "Media", 1, "", "", variaciones)

    def test_varias_variaciones(self):
        receta = self._receta("Versión vegetariana.\nVersión picante.")
        assert receta.variantes() == ["Versión vegetariana.", "Versión picante."]

    def test_sin_variaciones(self):
        assert self._receta("").variantes() == []

    def test_receta_sin_el_campo_no_tiene_variantes(self):
        # Las variaciones son opcionales: una receta sin ellas no rompe.
        assert Receta(1, "Test", "", 30, "Media", 1).variantes() == []

    def test_descarta_renglones_vacios_y_espacios(self):
        receta = self._receta("  Primera.  \n\n\n\t Segunda. \n")
        assert receta.variantes() == ["Primera.", "Segunda."]

    def test_preparacion_y_variaciones_son_independientes(self):
        receta = Receta(1, "Test", "", 30, "Media", 1, "", "Un paso.", "Una variante.")
        assert receta.pasos() == ["Un paso."]
        assert receta.variantes() == ["Una variante."]
