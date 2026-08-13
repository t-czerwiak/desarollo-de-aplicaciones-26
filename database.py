"""
Capa de persistencia para Chef Master Pro.
Gestiona la conexión a SQLite y todas las operaciones CRUD.
"""

import sqlite3
from typing import Optional

from models import Categoria, Ingrediente, Receta, RecetaIngrediente

DB_PATH = "chef_master.db"


# ---------------------------------------------------------------------------
# Conexión y creación del esquema
# ---------------------------------------------------------------------------


def get_connection() -> sqlite3.Connection:
    """Devuelve una conexión a la base de datos con row_factory configurada."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Crea las tablas si no existen e inserta datos de ejemplo."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS categorias (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre      TEXT    NOT NULL UNIQUE,
                descripcion TEXT    DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS recetas (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre              TEXT    NOT NULL,
                descripcion         TEXT    DEFAULT '',
                tiempo_preparacion  INTEGER NOT NULL DEFAULT 0,
                dificultad          TEXT    NOT NULL DEFAULT 'Media',
                categoria_id        INTEGER REFERENCES categorias(id) ON DELETE SET NULL,
                preparacion         TEXT    NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS ingredientes (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre          TEXT    NOT NULL UNIQUE,
                unidad          TEXT    NOT NULL DEFAULT 'g',
                precio_unitario REAL    NOT NULL DEFAULT 0.0,
                stock           REAL    NOT NULL DEFAULT 0.0
            );

            CREATE TABLE IF NOT EXISTS receta_ingredientes (
                receta_id       INTEGER NOT NULL REFERENCES recetas(id)     ON DELETE CASCADE,
                ingrediente_id  INTEGER NOT NULL REFERENCES ingredientes(id) ON DELETE CASCADE,
                cantidad        REAL    NOT NULL DEFAULT 0,
                PRIMARY KEY (receta_id, ingrediente_id)
            );
            """
        )
        _migrar_esquema(conn)
        primera_vez = _seed_data(conn)

    # Fuera del bloque anterior para que las categorías ya estén confirmadas
    # cuando el importador abra su propia conexión.
    if primera_vez:
        _importar_dataset_inicial()


def _migrar_esquema(conn: sqlite3.Connection) -> None:
    """
    Agrega al vuelo las columnas que falten en bases ya creadas.

    CREATE TABLE IF NOT EXISTS no modifica una tabla que ya existe, así que sin
    esto una base vieja se quedaría sin las columnas nuevas.
    """
    columnas = {row["name"] for row in conn.execute("PRAGMA table_info(recetas)")}
    if "preparacion" not in columnas:
        conn.execute("ALTER TABLE recetas ADD COLUMN preparacion TEXT NOT NULL DEFAULT ''")


def _importar_dataset_inicial() -> None:
    """Carga el dataset del CSV la primera vez que se arma la base."""
    import importar_datos  # diferido: importar_datos también importa este módulo

    try:
        importar_datos.importar_recetas_csv()
    except FileNotFoundError:
        pass  # sin el CSV la app igual arranca con los datos de ejemplo


def _seed_data(conn: sqlite3.Connection) -> bool:
    """
    Inserta datos de ejemplo sólo si las tablas están vacías.

    :returns: True si insertó los datos, False si la base ya tenía contenido.
    """
    if conn.execute("SELECT COUNT(*) FROM categorias").fetchone()[0] > 0:
        return False

    categorias = [
        ("Pasta", "Platos a base de pasta fresca o seca"),
        ("Carnes", "Preparaciones con carnes rojas, aves o pescados"),
        ("Postres", "Dulces, tortas y preparaciones azucaradas"),
        ("Sopas", "Caldos, cremas y sopas calientes o frías"),
        ("Ensaladas", "Preparaciones frías a base de vegetales"),
    ]
    conn.executemany(
        "INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)", categorias
    )

    ingredientes = [
        ("Harina", "g", 0.002, 5000),
        ("Huevo", "unidad", 0.30, 30),
        ("Manteca", "g", 0.005, 1000),
        ("Azúcar", "g", 0.001, 3000),
        ("Leche", "ml", 0.001, 4000),
        ("Tomate", "g", 0.003, 2000),
        ("Ajo", "g", 0.010, 500),
        ("Aceite de Oliva", "ml", 0.008, 1500),
        ("Sal", "g", 0.0005, 2000),
        ("Pimienta", "g", 0.020, 200),
        ("Pollo", "g", 0.006, 3000),
        ("Carne Molida", "g", 0.008, 2000),
        ("Queso Parmesano", "g", 0.015, 800),
        ("Albahaca", "g", 0.025, 300),
        ("Pasta Seca", "g", 0.003, 2500),
    ]
    conn.executemany(
        "INSERT INTO ingredientes (nombre, unidad, precio_unitario, stock) VALUES (?, ?, ?, ?)",
        ingredientes,
    )

    # Recuperar IDs generados
    cat = {r["nombre"]: r["id"] for r in conn.execute("SELECT id, nombre FROM categorias")}
    ing = {r["nombre"]: r["id"] for r in conn.execute("SELECT id, nombre FROM ingredientes")}

    recetas = [
        (
            "Spaghetti Bolognese", "Clásica pasta italiana con salsa de carne", 45, "Media", cat["Pasta"],
            "Hervir abundante agua con sal en una olla grande.\n"
            "Dorar la carne molida con el ajo picado y el aceite de oliva.\n"
            "Agregar el tomate y cocinar la salsa a fuego bajo 20 minutos.\n"
            "Cocinar la pasta seca hasta que esté al dente.\n"
            "Mezclar la pasta con la salsa y servir con parmesano rallado.",
        ),
        (
            "Tarta de Manzana", "Postre casero de manzana con masa quebrada", 90, "Alta", cat["Postres"],
            "Mezclar la harina con la manteca fría hasta lograr un arenado.\n"
            "Agregar el huevo y formar la masa. Descansar 30 minutos en la heladera.\n"
            "Estirar la masa y forrar un molde de tarta.\n"
            "Pelar las manzanas, cortarlas en gajos finos y acomodarlas en espiral.\n"
            "Espolvorear con azúcar y hornear 40 minutos a 180 grados.",
        ),
        (
            "Pollo al Limón", "Pechuga de pollo marinada con limón y hierbas", 35, "Baja", cat["Carnes"],
            "Marinar las pechugas con jugo de limón, ajo picado, sal y pimienta.\n"
            "Calentar el aceite de oliva en una sartén.\n"
            "Sellar el pollo 5 minutos de cada lado.\n"
            "Bajar el fuego y terminar la cocción tapado 15 minutos.\n"
            "Dejar reposar unos minutos antes de servir.",
        ),
        (
            "Sopa de Tomate", "Crema de tomate fresca con albahaca", 30, "Baja", cat["Sopas"],
            "Saltear el tomate cortado en cubos con aceite de oliva.\n"
            "Agregar agua caliente y sal. Cocinar 15 minutos.\n"
            "Procesar hasta obtener una crema lisa.\n"
            "Corregir la sal y sumar la albahaca fresca al final.",
        ),
        (
            "Ensalada César", "Ensalada con aderezo césar y crutones", 15, "Baja", cat["Ensaladas"],
            "Lavar y cortar la lechuga en trozos grandes.\n"
            "Preparar el aderezo con aceite de oliva, ajo y parmesano.\n"
            "Tostar los crutones en la sartén.\n"
            "Mezclar todo justo antes de servir para que no se ablande.",
        ),
    ]
    conn.executemany(
        "INSERT INTO recetas (nombre, descripcion, tiempo_preparacion, dificultad, categoria_id, preparacion) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        recetas,
    )

    rec = {r["nombre"]: r["id"] for r in conn.execute("SELECT id, nombre FROM recetas")}

    receta_ings = [
        # Spaghetti Bolognese
        (rec["Spaghetti Bolognese"], ing["Pasta Seca"], 200),
        (rec["Spaghetti Bolognese"], ing["Carne Molida"], 300),
        (rec["Spaghetti Bolognese"], ing["Tomate"], 200),
        (rec["Spaghetti Bolognese"], ing["Ajo"], 10),
        (rec["Spaghetti Bolognese"], ing["Aceite de Oliva"], 30),
        (rec["Spaghetti Bolognese"], ing["Queso Parmesano"], 50),
        # Tarta de Manzana
        (rec["Tarta de Manzana"], ing["Harina"], 250),
        (rec["Tarta de Manzana"], ing["Manteca"], 125),
        (rec["Tarta de Manzana"], ing["Azúcar"], 100),
        (rec["Tarta de Manzana"], ing["Huevo"], 2),
        # Pollo al Limón
        (rec["Pollo al Limón"], ing["Pollo"], 400),
        (rec["Pollo al Limón"], ing["Aceite de Oliva"], 20),
        (rec["Pollo al Limón"], ing["Ajo"], 5),
        (rec["Pollo al Limón"], ing["Sal"], 5),
        (rec["Pollo al Limón"], ing["Pimienta"], 2),
        # Sopa de Tomate
        (rec["Sopa de Tomate"], ing["Tomate"], 500),
        (rec["Sopa de Tomate"], ing["Albahaca"], 10),
        (rec["Sopa de Tomate"], ing["Aceite de Oliva"], 20),
        (rec["Sopa de Tomate"], ing["Sal"], 5),
        # Ensalada César
        (rec["Ensalada César"], ing["Aceite de Oliva"], 30),
        (rec["Ensalada César"], ing["Ajo"], 5),
        (rec["Ensalada César"], ing["Queso Parmesano"], 30),
    ]
    conn.executemany(
        "INSERT INTO receta_ingredientes (receta_id, ingrediente_id, cantidad) VALUES (?, ?, ?)",
        receta_ings,
    )
    return True


# ---------------------------------------------------------------------------
# CRUD – Categorias
# ---------------------------------------------------------------------------


def listar_categorias() -> list[Categoria]:
    """Retorna todas las categorías como objetos Categoria."""
    with get_connection() as conn:
        rows = conn.execute("SELECT id, nombre, descripcion FROM categorias ORDER BY nombre").fetchall()
    return [Categoria(r["id"], r["nombre"], r["descripcion"]) for r in rows]


def obtener_categoria(categoria_id: int) -> Optional[Categoria]:
    """Retorna una categoría por ID, o None si no existe."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, nombre, descripcion FROM categorias WHERE id = ?", (categoria_id,)
        ).fetchone()
    if row is None:
        return None
    return Categoria(row["id"], row["nombre"], row["descripcion"])


def crear_categoria(nombre: str, descripcion: str = "") -> Categoria:
    """Crea una nueva categoría y la devuelve."""
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion)
        )
        return Categoria(cur.lastrowid, nombre, descripcion)


def actualizar_categoria(categoria_id: int, nombre: str, descripcion: str = "") -> bool:
    """Actualiza una categoría por ID. Devuelve True si se modificó algún registro."""
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE categorias SET nombre = ?, descripcion = ? WHERE id = ?",
            (nombre, descripcion, categoria_id),
        )
        return cur.rowcount > 0


def eliminar_categoria(categoria_id: int) -> bool:
    """Elimina una categoría por ID. Devuelve True si se eliminó."""
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
        return cur.rowcount > 0


# ---------------------------------------------------------------------------
# CRUD – Ingredientes
# ---------------------------------------------------------------------------


def listar_ingredientes() -> list[Ingrediente]:
    """Retorna todos los ingredientes como objetos Ingrediente."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, nombre, unidad, precio_unitario, stock FROM ingredientes ORDER BY nombre"
        ).fetchall()
    return [Ingrediente(r["id"], r["nombre"], r["unidad"], r["precio_unitario"], r["stock"]) for r in rows]


def obtener_ingrediente(ingrediente_id: int) -> Optional[Ingrediente]:
    """Retorna un ingrediente por ID, o None si no existe."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, nombre, unidad, precio_unitario, stock FROM ingredientes WHERE id = ?",
            (ingrediente_id,),
        ).fetchone()
    if row is None:
        return None
    return Ingrediente(row["id"], row["nombre"], row["unidad"], row["precio_unitario"], row["stock"])


def crear_ingrediente(nombre: str, unidad: str, precio_unitario: float, stock: float) -> Ingrediente:
    """Crea un nuevo ingrediente y lo devuelve."""
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO ingredientes (nombre, unidad, precio_unitario, stock) VALUES (?, ?, ?, ?)",
            (nombre, unidad, precio_unitario, stock),
        )
        return Ingrediente(cur.lastrowid, nombre, unidad, precio_unitario, stock)


def actualizar_ingrediente(
    ingrediente_id: int, nombre: str, unidad: str, precio_unitario: float, stock: float
) -> bool:
    """Actualiza un ingrediente por ID. Devuelve True si se modificó."""
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE ingredientes SET nombre=?, unidad=?, precio_unitario=?, stock=? WHERE id=?",
            (nombre, unidad, precio_unitario, stock, ingrediente_id),
        )
        return cur.rowcount > 0


def eliminar_ingrediente(ingrediente_id: int) -> bool:
    """Elimina un ingrediente por ID. Devuelve True si se eliminó."""
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM ingredientes WHERE id = ?", (ingrediente_id,))
        return cur.rowcount > 0


# ---------------------------------------------------------------------------
# CRUD – Recetas
# ---------------------------------------------------------------------------


def listar_recetas(
    categoria_id: Optional[int] = None,
    tiempo_max: Optional[int] = None,
    dificultad: Optional[str] = None,
) -> list[Receta]:
    """
    Retorna recetas con filtros opcionales.

    :param categoria_id: Filtra por categoría.
    :param tiempo_max:   Filtra recetas con tiempo de preparación <= tiempo_max.
    :param dificultad:   Filtra por nivel de dificultad ('Baja', 'Media', 'Alta').
    """
    query = """
        SELECT r.id, r.nombre, r.descripcion, r.tiempo_preparacion,
               r.dificultad, r.categoria_id, r.preparacion,
               COALESCE(c.nombre, '') AS categoria_nombre
        FROM recetas r
        LEFT JOIN categorias c ON r.categoria_id = c.id
        WHERE 1=1
    """
    params: list = []
    if categoria_id is not None:
        query += " AND r.categoria_id = ?"
        params.append(categoria_id)
    if tiempo_max is not None:
        query += " AND r.tiempo_preparacion <= ?"
        params.append(tiempo_max)
    if dificultad:
        query += " AND r.dificultad = ?"
        params.append(dificultad)
    query += " ORDER BY r.nombre"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    recetas = []
    for r in rows:
        receta = Receta(
            r["id"],
            r["nombre"],
            r["descripcion"],
            r["tiempo_preparacion"],
            r["dificultad"],
            r["categoria_id"],
            r["categoria_nombre"],
            r["preparacion"],
        )
        recetas.append(receta)
    return recetas


def obtener_receta(receta_id: int) -> Optional[Receta]:
    """Retorna una receta por ID con sus ingredientes cargados, o None si no existe."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT r.id, r.nombre, r.descripcion, r.tiempo_preparacion,
                   r.dificultad, r.categoria_id, r.preparacion,
                   COALESCE(c.nombre, '') AS categoria_nombre
            FROM recetas r
            LEFT JOIN categorias c ON r.categoria_id = c.id
            WHERE r.id = ?
            """,
            (receta_id,),
        ).fetchone()
        if row is None:
            return None
        receta = Receta(
            row["id"],
            row["nombre"],
            row["descripcion"],
            row["tiempo_preparacion"],
            row["dificultad"],
            row["categoria_id"],
            row["categoria_nombre"],
            row["preparacion"],
        )
        ing_rows = conn.execute(
            """
            SELECT i.id, i.nombre, i.unidad, i.precio_unitario, i.stock, ri.cantidad
            FROM receta_ingredientes ri
            JOIN ingredientes i ON ri.ingrediente_id = i.id
            WHERE ri.receta_id = ?
            """,
            (receta_id,),
        ).fetchall()
        for ir in ing_rows:
            ing = Ingrediente(ir["id"], ir["nombre"], ir["unidad"], ir["precio_unitario"], ir["stock"])
            receta.agregar_ingrediente(ing, ir["cantidad"])
    return receta


def crear_receta(
    nombre: str,
    descripcion: str,
    tiempo_preparacion: int,
    dificultad: str,
    categoria_id: Optional[int],
    ingredientes: list[tuple[int, float]],
    preparacion: str = "",
) -> Receta:
    """
    Crea una receta con sus ingredientes asociados.

    :param ingredientes: Lista de tuplas (ingrediente_id, cantidad).
    :param preparacion:  Pasos de preparación, uno por renglón.
    """
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO recetas (nombre, descripcion, tiempo_preparacion, dificultad, categoria_id, preparacion) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (nombre, descripcion, tiempo_preparacion, dificultad, categoria_id, preparacion),
        )
        receta_id = cur.lastrowid
        if ingredientes:
            conn.executemany(
                "INSERT INTO receta_ingredientes (receta_id, ingrediente_id, cantidad) VALUES (?, ?, ?)",
                [(receta_id, ing_id, cant) for ing_id, cant in ingredientes],
            )
    return obtener_receta(receta_id)


def actualizar_receta(
    receta_id: int,
    nombre: str,
    descripcion: str,
    tiempo_preparacion: int,
    dificultad: str,
    categoria_id: Optional[int],
    ingredientes: list[tuple[int, float]],
    preparacion: str = "",
) -> bool:
    """
    Actualiza una receta y reemplaza sus ingredientes.

    :param ingredientes: Lista de tuplas (ingrediente_id, cantidad).
    :param preparacion:  Pasos de preparación, uno por renglón.
    :returns: True si se actualizó el registro.
    """
    with get_connection() as conn:
        cur = conn.execute(
            """
            UPDATE recetas
            SET nombre=?, descripcion=?, tiempo_preparacion=?, dificultad=?,
                categoria_id=?, preparacion=?
            WHERE id=?
            """,
            (nombre, descripcion, tiempo_preparacion, dificultad, categoria_id, preparacion, receta_id),
        )
        if cur.rowcount == 0:
            return False
        conn.execute("DELETE FROM receta_ingredientes WHERE receta_id = ?", (receta_id,))
        if ingredientes:
            conn.executemany(
                "INSERT INTO receta_ingredientes (receta_id, ingrediente_id, cantidad) VALUES (?, ?, ?)",
                [(receta_id, ing_id, cant) for ing_id, cant in ingredientes],
            )
    return True


def eliminar_receta(receta_id: int) -> bool:
    """Elimina una receta por ID (los ingredientes asociados se eliminan en cascada)."""
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM recetas WHERE id = ?", (receta_id,))
        return cur.rowcount > 0
