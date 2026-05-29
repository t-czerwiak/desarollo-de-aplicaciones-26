"""
Módulo de clases del dominio para Chef Master Pro.
Define las entidades: Categoria, Ingrediente y Receta.
"""


class Categoria:
    """Representa una categoría de cocina (ej: Pasta, Carnes, Postres)."""

    def __init__(self, id: int, nombre: str, descripcion: str = ""):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion

    def descripcion_completa(self) -> str:
        """Devuelve una descripción legible de la categoría."""
        if self.descripcion:
            return f"{self.nombre}: {self.descripcion}"
        return self.nombre

    def __str__(self) -> str:
        return self.nombre

    def __repr__(self) -> str:
        return f"Categoria(id={self.id}, nombre='{self.nombre}')"


class Ingrediente:
    """Representa un ingrediente del inventario."""

    def __init__(
        self,
        id: int,
        nombre: str,
        unidad: str,
        precio_unitario: float,
        stock: float,
    ):
        self.id = id
        self.nombre = nombre
        self.unidad = unidad
        self.precio_unitario = precio_unitario
        self.stock = stock

    def costo_estimado(self, cantidad: float) -> float:
        """Calcula el costo estimado de una cantidad dada del ingrediente."""
        if cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa.")
        return round(self.precio_unitario * cantidad, 2)

    def es_disponible(self, cantidad_requerida: float = 0) -> bool:
        """Indica si hay suficiente stock disponible."""
        return self.stock >= cantidad_requerida

    def __str__(self) -> str:
        return f"{self.nombre} ({self.stock} {self.unidad})"

    def __repr__(self) -> str:
        return (
            f"Ingrediente(id={self.id}, nombre='{self.nombre}', "
            f"stock={self.stock} {self.unidad})"
        )


class RecetaIngrediente:
    """Asociación entre una receta y un ingrediente con su cantidad."""

    def __init__(self, ingrediente: Ingrediente, cantidad: float):
        self.ingrediente = ingrediente
        self.cantidad = cantidad

    def costo(self) -> float:
        """Costo de este ingrediente en la receta."""
        return self.ingrediente.costo_estimado(self.cantidad)

    def __str__(self) -> str:
        return f"{self.ingrediente.nombre}: {self.cantidad} {self.ingrediente.unidad}"


class Receta:
    """Representa una receta culinaria."""

    TIEMPO_COMPLEJO_MINUTOS = 60

    def __init__(
        self,
        id: int,
        nombre: str,
        descripcion: str,
        tiempo_preparacion: int,
        dificultad: str,
        categoria_id: int,
        categoria_nombre: str = "",
    ):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.tiempo_preparacion = tiempo_preparacion
        self.dificultad = dificultad
        self.categoria_id = categoria_id
        self.categoria_nombre = categoria_nombre
        self.ingredientes: list[RecetaIngrediente] = []

    def es_compleja(self) -> bool:
        """Determina si la receta es compleja según su tiempo de preparación."""
        return self.tiempo_preparacion >= self.TIEMPO_COMPLEJO_MINUTOS

    def tiempo_formateado(self) -> str:
        """Devuelve el tiempo de preparación en formato legible (horas y minutos)."""
        horas = self.tiempo_preparacion // 60
        minutos = self.tiempo_preparacion % 60
        if horas > 0:
            return f"{horas}h {minutos}min" if minutos else f"{horas}h"
        return f"{minutos}min"

    def costo_total(self) -> float:
        """Calcula el costo total estimado de todos los ingredientes de la receta."""
        return round(sum(ri.costo() for ri in self.ingredientes), 2)

    def agregar_ingrediente(self, ingrediente: Ingrediente, cantidad: float) -> None:
        """Agrega un ingrediente con su cantidad a la receta."""
        self.ingredientes.append(RecetaIngrediente(ingrediente, cantidad))

    def __str__(self) -> str:
        return self.nombre

    def __repr__(self) -> str:
        return (
            f"Receta(id={self.id}, nombre='{self.nombre}', "
            f"tiempo={self.tiempo_preparacion}min)"
        )
