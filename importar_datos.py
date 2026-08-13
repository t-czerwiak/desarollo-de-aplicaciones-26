"""
Importación de datos desde CSV para Chef Master Pro.

Lee el dataset de recetas con Pandas y da de alta cada fila usando la misma
función de alta que usa el resto de la aplicación (database.crear_receta).

Se puede correr desde la app (sección Estadísticas) o por consola:

    python importar_datos.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

import database as db

CSV_RECETAS = Path(__file__).parent / "datos" / "recetas.csv"


def _mapa_categorias() -> dict[str, int]:
    """Devuelve {nombre_categoria: id} para resolver la columna 'categoria' del CSV."""
    return {c.nombre.lower(): c.id for c in db.listar_categorias()}


def importar_recetas_csv(ruta: Path | str = CSV_RECETAS) -> tuple[int, int]:
    """
    Lee el CSV con pandas.read_csv() y crea una receta por cada fila.

    Recorre el DataFrame con un for y llama a db.crear_receta(), que es la
    misma función de alta que usa el formulario de "Nueva Receta".

    :param ruta: Ubicación del archivo CSV a importar.
    :returns: Tupla (importadas, omitidas_por_duplicado).
    """
    df = pd.read_csv(ruta)

    categorias = _mapa_categorias()
    # Nombres ya cargados, para que correr el importador dos veces no duplique todo.
    existentes = {r.nombre.lower() for r in db.listar_recetas()}

    importadas = 0
    omitidas = 0

    for _, fila in df.iterrows():
        nombre = str(fila["nombre"]).strip()

        if nombre.lower() in existentes:
            omitidas += 1
            continue

        categoria_id = categorias.get(str(fila["categoria"]).strip().lower())

        db.crear_receta(
            nombre,
            str(fila["descripcion"]).strip(),
            int(fila["tiempo_preparacion"]),
            str(fila["dificultad"]).strip(),
            categoria_id,
            [],  # el CSV describe la receta, no su lista de ingredientes
        )

        existentes.add(nombre.lower())
        importadas += 1

    return importadas, omitidas


if __name__ == "__main__":
    db.init_db()
    nuevas, repetidas = importar_recetas_csv()
    print(f"Recetas importadas:              {nuevas}")
    print(f"Omitidas por estar ya cargadas:  {repetidas}")
    print(f"Total de recetas en la base:     {len(db.listar_recetas())}")
