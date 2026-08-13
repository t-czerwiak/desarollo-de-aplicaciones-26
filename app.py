"""
Chef Master Pro – Aplicación principal de Streamlit.
Sistema de Gestión del Instituto ORT Cuisine.
"""

import pandas as pd
import streamlit as st

import database as db
import importar_datos

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Chef Master Pro",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializar la base de datos (crea tablas e inserta datos de ejemplo si es necesario)
db.init_db()

# ---------------------------------------------------------------------------
# Estilo visual personalizado
# ---------------------------------------------------------------------------

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600;1,700&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --gold:        #C8913A;
    --gold-light:  #E0AC5A;
    --gold-muted:  rgba(200,145,58,0.12);
    --bg:          #0F0E0B;
    --bg-card:     #181511;
    --border:      rgba(200,145,58,0.22);
    --border-sub:  rgba(255,255,255,0.06);
    --text:        #F0EBE1;
    --text-muted:  #7A7068;
}

/* ── Base ── */
html, .stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    font-family: 'DM Sans', sans-serif !important;
    letter-spacing: 0.025em;
}

[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

/* ── Tipografía ── */
h1, h2, h3, h4 {
    font-family: 'Playfair Display', serif !important;
    letter-spacing: 0.04em;
}

h1 {
    font-size: 2.6rem !important;
    font-weight: 700 !important;
    border-bottom: 1px solid var(--gold) !important;
    padding-bottom: 0.35em !important;
    margin-bottom: 1.2em !important;
    line-height: 1.2 !important;
    color: var(--text) !important;
}

h2 {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
}

h3 {
    font-size: 1.2rem !important;
    font-weight: 500 !important;
    color: var(--text) !important;
}

/* Subheader con acento lateral dorado */
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3 {
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important;
    border-left: 3px solid var(--gold) !important;
    padding-left: 0.65em !important;
    color: var(--text) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0D0C0A !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] h1 {
    font-family: 'Playfair Display', serif !important;
    color: var(--gold) !important;
    border-bottom: 1px solid var(--border) !important;
    font-size: 1.9rem !important;
    font-weight: 300 !important;
    letter-spacing: 0.1em !important;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text) !important;
    transition: color 0.2s ease;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    color: var(--gold) !important;
}

[data-testid="stSidebar"] [data-testid="stInfo"],
[data-testid="stSidebar"] [data-testid="stAlert"] {
    background: rgba(200,145,58,0.07) !important;
    border: none !important;
    border-left: 2px solid var(--gold) !important;
    border-radius: 1px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.06em !important;
    color: var(--text-muted) !important;
}

/* ── Tabs ──
   Streamlit cambió las pestañas de BaseWeb a React Aria: las versiones viejas
   las marcan con data-baseweb="tab" y las nuevas con data-testid="stTab".
   Se estilan las dos para que se vea igual en local y en el deploy. */
.stTabs [data-baseweb="tab-list"],
.stTabs [role="tablist"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}

.stTabs [data-baseweb="tab"],
.stTabs [data-testid="stTab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    background: transparent !important;
    border: none !important;
    padding: 0.65em 1.5em !important;
    transition: color 0.2s ease !important;
}

.stTabs [data-baseweb="tab"]:hover,
.stTabs [data-testid="stTab"]:hover {
    color: var(--text) !important;
    background: var(--gold-muted) !important;
}

.stTabs [aria-selected="true"][data-baseweb="tab"],
.stTabs [data-testid="stTab"][aria-selected="true"] {
    color: var(--gold) !important;
    background: transparent !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    background-color: var(--gold) !important;
    height: 2px !important;
}

/* La versión nueva no tiene el elemento tab-highlight, así que el subrayado
   de la pestaña activa se dibuja sobre la pestaña misma. */
.stTabs [data-testid="stTab"][aria-selected="true"] {
    box-shadow: inset 0 -2px 0 var(--gold) !important;
}

.stTabs [data-baseweb="tab-border"] { display: none !important; }

.stTabs [data-baseweb="tab-panel"],
.stTabs [role="tabpanel"] {
    padding-top: 1.5em !important;
}

/* ── Botones ── */
.stButton > button,
[data-testid="stFormSubmitButton"] > button {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    transition: all 0.2s ease !important;
}

.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button[kind="primary"] {
    background: var(--gold) !important;
    border-color: var(--gold) !important;
    color: #0A0908 !important;
}

.stButton > button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
    background: var(--gold-light) !important;
    border-color: var(--gold-light) !important;
    box-shadow: 0 0 18px rgba(200,145,58,0.35) !important;
    transform: translateY(-1px) !important;
}

.stButton > button:not([kind="primary"]):hover {
    border-color: var(--gold) !important;
    color: var(--gold) !important;
    background: var(--gold-muted) !important;
}

/* ── Inputs ── */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-sub) !important;
    color: var(--text) !important;
    border-radius: 2px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.03em !important;
    transition: border-color 0.2s ease !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 1px rgba(200,145,58,0.4) !important;
}

/* Selectbox */
[data-baseweb="select"] > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-sub) !important;
    color: var(--text) !important;
    border-radius: 2px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    transition: border-color 0.2s ease !important;
}

[data-baseweb="select"] > div:hover {
    border-color: var(--gold) !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"] {
    background: #1C1913 !important;
    border: 1px solid var(--border) !important;
    border-radius: 2px !important;
}

[data-baseweb="option"]:hover {
    background: var(--gold-muted) !important;
}

/* Labels */
.stTextInput label p,
.stSelectbox label p,
.stNumberInput label p,
.stTextArea label p,
.stCheckbox label p,
[data-testid="stWidgetLabel"] p {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-sub) !important;
    border-radius: 2px !important;
    margin-bottom: 0.5em !important;
    transition: border-color 0.2s ease !important;
}

[data-testid="stExpander"]:hover {
    border-color: var(--border) !important;
}

[data-testid="stExpander"] summary {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.76rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 0.85em 1em !important;
    color: var(--text) !important;
}

[data-testid="stExpanderDetails"] {
    border-top: 1px solid var(--border-sub) !important;
    padding: 1em 1.2em !important;
}

/* ── Métricas ── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-sub) !important;
    border-left: 3px solid var(--gold) !important;
    border-radius: 2px !important;
    padding: 0.9em 1.1em !important;
}

[data-testid="stMetricLabel"] p {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    color: var(--gold) !important;
}

/* ── Tablas ── */
.stTable table {
    border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.04em !important;
    width: 100% !important;
}

.stTable th {
    background: rgba(200,145,58,0.1) !important;
    color: var(--gold) !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    font-size: 0.65rem !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 0.65em 0.9em !important;
}

.stTable td {
    border-bottom: 1px solid var(--border-sub) !important;
    color: var(--text) !important;
    padding: 0.55em 0.9em !important;
}

.stTable tr:hover td {
    background: var(--gold-muted) !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5em 0 !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    border-radius: 2px !important;
    border: none !important;
    border-left: 3px solid !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.04em !important;
}

/* ── Caption ── */
[data-testid="stCaptionContainer"] p {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

/* ── Texto general ── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    font-family: 'DM Sans', sans-serif !important;
    line-height: 1.75 !important;
    color: var(--text) !important;
    font-size: 0.88rem !important;
}

/* ── Contenedor principal ── */
[data-testid="block-container"] {
    padding-top: 2.5rem !important;
    max-width: 1200px !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold); }

/* ── Checkbox ── */
[data-testid="stCheckbox"] label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.04em !important;
    color: var(--text) !important;
}

/* ── Form container ── */
[data-testid="stForm"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-sub) !important;
    border-radius: 2px !important;
    padding: 1.5em !important;
}
"""

st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DIFICULTADES = ["Baja", "Media", "Alta"]

# Etiquetas del menú lateral. Se usan tanto para dibujar el menú como para
# decidir qué sección mostrar, así no vuelven a quedar desincronizadas.
SEC_RECETAS = "📋 Recetas"
SEC_INGREDIENTES = "🥦 Ingredientes"
SEC_CATEGORIAS = "🗂️ Categorías"
SEC_ESTADISTICAS = "📊 Estadísticas"


def _show_success(msg: str) -> None:
    st.success(msg)
    st.rerun()


def _interpretar_tiempos(tiempos: pd.Series) -> str:
    """
    Arma el párrafo que interpreta las medidas de tendencia central.

    Se calcula sobre los datos reales en vez de dejarlo escrito a mano, así el
    texto sigue siendo cierto aunque se carguen o borren recetas.
    """
    media = tiempos.mean()
    mediana = tiempos.median()
    moda = tiempos.mode()

    # Cuánto se corre la media respecto de la mediana, en proporción a la mediana.
    diferencia = media - mediana
    desvio_relativo = abs(diferencia) / mediana * 100 if mediana else 0

    if desvio_relativo < 5:
        forma = (
            f"La media ({media:.2f} min) y la mediana ({mediana:.0f} min) son casi iguales, "
            "así que los tiempos de preparación se reparten de forma bastante simétrica: "
            "no hay recetas extremas que arrastren el promedio para ningún lado."
        )
    elif diferencia > 0:
        forma = (
            f"La media ({media:.2f} min) es más alta que la mediana ({mediana:.0f} min). "
            "Eso pasa porque unas pocas recetas muy largas empujan el promedio hacia arriba, "
            "mientras que la mitad del recetario se prepara en "
            f"{mediana:.0f} minutos o menos. En un caso así la mediana describe mejor "
            "a la receta típica que la media."
        )
    else:
        forma = (
            f"La media ({media:.2f} min) es más baja que la mediana ({mediana:.0f} min): "
            "hay un grupo de recetas muy rápidas que tira el promedio hacia abajo, "
            "aunque la mayoría de las preparaciones lleve más tiempo que eso."
        )

    repeticiones = int((tiempos == moda.iloc[0]).sum())
    veces = "vez" if repeticiones == 1 else "veces"

    if len(moda) > 1:
        valores = " y ".join(f"{v:.0f} min" for v in moda)
        claridad = (
            f"No hay una moda única: {valores} se repiten la misma cantidad de veces "
            f"({repeticiones} cada uno), así que los valores están bastante repartidos "
            "y ningún tiempo domina al resto."
        )
    elif repeticiones <= 2:
        claridad = (
            f"La moda es {moda.iloc[0]:.0f} min, pero aparece apenas {repeticiones} {veces} "
            f"sobre {len(tiempos)} recetas: casi todos los tiempos son distintos, "
            "por lo que la moda no aporta demasiado en este conjunto."
        )
    else:
        claridad = (
            f"La moda es clara: {moda.iloc[0]:.0f} min aparece {repeticiones} {veces} "
            f"sobre {len(tiempos)} recetas, o sea que es la duración más habitual "
            "a la hora de planificar la cocina."
        )

    return f"{forma} {claridad}"


# ---------------------------------------------------------------------------
# Sidebar – Navegación
# ---------------------------------------------------------------------------

st.sidebar.title("🍳 Chef Master Pro")
st.sidebar.caption("Instituto ORT Cuisine")
st.sidebar.divider()

seccion = st.sidebar.radio(
    "Menú principal",
    options=[SEC_RECETAS, SEC_INGREDIENTES, SEC_CATEGORIAS, SEC_ESTADISTICAS],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.info("Sistema de Gestión Gastronómica\n\nInstituto ORT Cuisine © 2024")

# ===========================================================================
# SECCIÓN: RECETAS
# ===========================================================================

if seccion == SEC_RECETAS:
    st.title("Gestión de Recetas")

    tab_lista, tab_nueva, tab_editar, tab_eliminar = st.tabs(
        ["Listado", "Nueva Receta", "Editar", "Eliminar"]
    )

    # -----------------------------------------------------------------------
    # Tab: Listado con filtros
    # -----------------------------------------------------------------------
    with tab_lista:
        st.subheader("Recetas disponibles")

        col1, col2, col3 = st.columns(3)
        categorias = db.listar_categorias()
        opciones_cat = {c.nombre: c.id for c in categorias}

        with col1:
            filtro_cat = st.selectbox(
                "Filtrar por categoría",
                options=["Todas"] + list(opciones_cat.keys()),
                key="filtro_cat_recetas",
            )
        with col2:
            filtro_tiempo = st.number_input(
                "Tiempo máximo (min)",
                min_value=0,
                max_value=480,
                value=0,
                step=5,
                key="filtro_tiempo_recetas",
            )
        with col3:
            filtro_dif = st.selectbox(
                "Filtrar por dificultad",
                options=["Todas"] + DIFICULTADES,
                key="filtro_dif_recetas",
            )

        cat_id_filtro = opciones_cat.get(filtro_cat) if filtro_cat != "Todas" else None
        tiempo_filtro = filtro_tiempo if filtro_tiempo > 0 else None
        dif_filtro = filtro_dif if filtro_dif != "Todas" else None

        recetas = db.listar_recetas(
            categoria_id=cat_id_filtro,
            tiempo_max=tiempo_filtro,
            dificultad=dif_filtro,
        )

        if not recetas:
            st.info("No se encontraron recetas con los filtros aplicados.")
        else:
            st.caption(f"Se encontraron **{len(recetas)}** receta(s).")
            for receta in recetas:
                with st.expander(
                    f"{'🔴' if receta.es_compleja() else '🟢'} {receta.nombre} "
                    f"— {receta.categoria_nombre} | {receta.tiempo_formateado()}"
                ):
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"**Descripción:** {receta.descripcion or '—'}")
                        st.write(f"**Categoría:** {receta.categoria_nombre or '—'}")
                    with col_b:
                        st.metric("Tiempo", receta.tiempo_formateado())
                        st.write(receta.dificultad)
                        if receta.es_compleja():
                            st.caption("Receta compleja")

                    # Cargar ingredientes al expandir
                    receta_detalle = db.obtener_receta(receta.id)
                    if receta_detalle and receta_detalle.ingredientes:
                        st.write("**Ingredientes:**")
                        datos_ings = [
                            {
                                "Ingrediente": ri.ingrediente.nombre,
                                "Cantidad": f"{ri.cantidad} {ri.ingrediente.unidad}",
                                "Costo Est.": f"${ri.costo():.2f}",
                            }
                            for ri in receta_detalle.ingredientes
                        ]
                        st.table(datos_ings)
                        st.write(f"**Costo total estimado:** ${receta_detalle.costo_total():.2f}")

    # -----------------------------------------------------------------------
    # Tab: Nueva receta
    # -----------------------------------------------------------------------
    with tab_nueva:
        st.subheader("Registrar nueva receta")

        categorias = db.listar_categorias()
        opciones_cat_nueva = {c.nombre: c.id for c in categorias}
        ingredientes_todos = db.listar_ingredientes()

        with st.form("form_nueva_receta"):
            nombre = st.text_input("Nombre de la receta *")
            descripcion = st.text_area("Descripción")
            col1, col2, col3 = st.columns(3)
            with col1:
                tiempo = st.number_input("Tiempo de preparación (min) *", min_value=1, max_value=480, value=30)
            with col2:
                dificultad = st.selectbox("Dificultad *", DIFICULTADES, index=1)
            with col3:
                categoria_sel = st.selectbox(
                    "Categoría",
                    options=["— Sin categoría —"] + list(opciones_cat_nueva.keys()),
                )

            st.divider()
            st.write("**Ingredientes**")
            st.caption("Seleccioná los ingredientes y sus cantidades.")

            ingredientes_seleccionados = []
            if ingredientes_todos:
                cols = st.columns(2)
                for i, ing in enumerate(ingredientes_todos):
                    col = cols[i % 2]
                    with col:
                        usar = st.checkbox(f"{ing.nombre} ({ing.unidad})", key=f"nueva_ing_{ing.id}")
                        if usar:
                            cant = st.number_input(
                                f"Cantidad ({ing.unidad})",
                                min_value=0.01,
                                value=1.0,
                                step=0.5,
                                key=f"nueva_cant_{ing.id}",
                            )
                            ingredientes_seleccionados.append((ing.id, cant))
            else:
                st.info("No hay ingredientes registrados. Agregá ingredientes primero.")

            submitted = st.form_submit_button("Guardar receta", type="primary")

        if submitted:
            errores = []
            if not nombre.strip():
                errores.append("El nombre no puede estar vacío.")
            if tiempo <= 0:
                errores.append("El tiempo de preparación debe ser mayor a 0.")

            if errores:
                for e in errores:
                    st.error(e)
            else:
                cat_id = opciones_cat_nueva.get(categoria_sel)
                db.crear_receta(
                    nombre.strip(),
                    descripcion.strip(),
                    tiempo,
                    dificultad,
                    cat_id,
                    ingredientes_seleccionados,
                )
                _show_success(f"Receta '{nombre.strip()}' creada correctamente.")

    # -----------------------------------------------------------------------
    # Tab: Editar receta
    # -----------------------------------------------------------------------
    with tab_editar:
        st.subheader("Editar receta existente")

        recetas_lista = db.listar_recetas()
        if not recetas_lista:
            st.info("No hay recetas para editar.")
        else:
            opciones_recetas = {r.nombre: r.id for r in recetas_lista}
            sel_nombre = st.selectbox("Seleccioná una receta", list(opciones_recetas.keys()), key="editar_sel_receta")
            receta_ed = db.obtener_receta(opciones_recetas[sel_nombre])

            if receta_ed:
                categorias = db.listar_categorias()
                opciones_cat_ed = {c.nombre: c.id for c in categorias}
                ingredientes_todos = db.listar_ingredientes()

                ids_actuales = {ri.ingrediente.id: ri.cantidad for ri in receta_ed.ingredientes}

                with st.form("form_editar_receta"):
                    nombre_ed = st.text_input("Nombre *", value=receta_ed.nombre)
                    desc_ed = st.text_area("Descripción", value=receta_ed.descripcion)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        tiempo_ed = st.number_input(
                            "Tiempo (min) *",
                            min_value=1,
                            max_value=480,
                            value=receta_ed.tiempo_preparacion,
                        )
                    with col2:
                        dif_idx = DIFICULTADES.index(receta_ed.dificultad) if receta_ed.dificultad in DIFICULTADES else 1
                        dif_ed = st.selectbox("Dificultad *", DIFICULTADES, index=dif_idx)
                    with col3:
                        cat_opciones_ed = ["— Sin categoría —"] + list(opciones_cat_ed.keys())
                        cat_actual_idx = 0
                        if receta_ed.categoria_nombre in opciones_cat_ed:
                            cat_actual_idx = cat_opciones_ed.index(receta_ed.categoria_nombre)
                        cat_ed = st.selectbox("Categoría", cat_opciones_ed, index=cat_actual_idx)

                    st.divider()
                    st.write("**Ingredientes**")
                    nuevos_ings = []
                    if ingredientes_todos:
                        cols = st.columns(2)
                        for i, ing in enumerate(ingredientes_todos):
                            col = cols[i % 2]
                            with col:
                                esta = ing.id in ids_actuales
                                usar = st.checkbox(
                                    f"{ing.nombre} ({ing.unidad})",
                                    value=esta,
                                    key=f"ed_ing_{ing.id}",
                                )
                                if usar:
                                    cant_def = float(ids_actuales.get(ing.id, 1.0))
                                    cant = st.number_input(
                                        f"Cantidad ({ing.unidad})",
                                        min_value=0.01,
                                        value=cant_def,
                                        step=0.5,
                                        key=f"ed_cant_{ing.id}",
                                    )
                                    nuevos_ings.append((ing.id, cant))

                    submitted_ed = st.form_submit_button("Guardar cambios", type="primary")

                if submitted_ed:
                    errores = []
                    if not nombre_ed.strip():
                        errores.append("El nombre no puede estar vacío.")
                    if tiempo_ed <= 0:
                        errores.append("El tiempo debe ser mayor a 0.")

                    if errores:
                        for e in errores:
                            st.error(e)
                    else:
                        cat_id_ed = opciones_cat_ed.get(cat_ed)
                        ok = db.actualizar_receta(
                            receta_ed.id,
                            nombre_ed.strip(),
                            desc_ed.strip(),
                            tiempo_ed,
                            dif_ed,
                            cat_id_ed,
                            nuevos_ings,
                        )
                        if ok:
                            _show_success(f"Receta '{nombre_ed.strip()}' actualizada correctamente.")
                        else:
                            st.error("No se pudo actualizar la receta.")

    # -----------------------------------------------------------------------
    # Tab: Eliminar receta
    # -----------------------------------------------------------------------
    with tab_eliminar:
        st.subheader("Eliminar receta")

        recetas_lista = db.listar_recetas()
        if not recetas_lista:
            st.info("No hay recetas para eliminar.")
        else:
            opciones_del = {r.nombre: r.id for r in recetas_lista}
            sel_del = st.selectbox("Seleccioná la receta a eliminar", list(opciones_del.keys()), key="del_receta")

            receta_del = db.obtener_receta(opciones_del[sel_del])
            if receta_del:
                st.warning(
                    f"Estás por eliminar **{receta_del.nombre}** "
                    f"(categoría: {receta_del.categoria_nombre or '—'}). "
                    f"Esta acción no se puede deshacer."
                )
                if st.button("Confirmar eliminación", type="primary", key="btn_del_receta"):
                    ok = db.eliminar_receta(receta_del.id)
                    if ok:
                        _show_success(f"Receta '{receta_del.nombre}' eliminada.")
                    else:
                        st.error("No se pudo eliminar la receta.")

# ===========================================================================
# SECCIÓN: INGREDIENTES
# ===========================================================================

elif seccion == SEC_INGREDIENTES:
    st.title("Inventario de Ingredientes")

    tab_lista, tab_nuevo, tab_editar, tab_eliminar = st.tabs(
        ["Listado", "Nuevo Ingrediente", "Editar", "Eliminar"]
    )

    # -----------------------------------------------------------------------
    # Tab: Listado con filtros
    # -----------------------------------------------------------------------
    with tab_lista:
        st.subheader("Inventario actual")

        col1, col2 = st.columns(2)
        with col1:
            busqueda = st.text_input("Buscar por nombre", key="busq_ing")
        with col2:
            solo_disponibles = st.checkbox("Solo con stock disponible", key="filtro_stock")

        ingredientes = db.listar_ingredientes()

        # Filtrar en Python usando los objetos del dominio
        if busqueda:
            ingredientes = [i for i in ingredientes if busqueda.lower() in i.nombre.lower()]
        if solo_disponibles:
            ingredientes = [i for i in ingredientes if i.es_disponible(0.01)]

        if not ingredientes:
            st.info("No se encontraron ingredientes con los filtros aplicados.")
        else:
            st.caption(f"Se muestran **{len(ingredientes)}** ingrediente(s).")
            datos = [
                {
                    "Nombre": ing.nombre,
                    "Unidad": ing.unidad,
                    "Stock": f"{ing.stock} {ing.unidad}",
                    "Precio/Unidad": f"${ing.precio_unitario:.4f}",
                    "Disponible": "Sí" if ing.es_disponible(0.01) else "No",
                    "Costo (100 u.)": f"${ing.costo_estimado(100):.2f}",
                }
                for ing in ingredientes
            ]
            st.dataframe(datos, use_container_width=True)

    # -----------------------------------------------------------------------
    # Tab: Nuevo ingrediente
    # -----------------------------------------------------------------------
    with tab_nuevo:
        st.subheader("Registrar nuevo ingrediente")

        with st.form("form_nuevo_ing"):
            col1, col2 = st.columns(2)
            with col1:
                nombre_ing = st.text_input("Nombre del ingrediente *")
                unidad_ing = st.text_input("Unidad de medida *", placeholder="g, ml, unidad, kg…")
            with col2:
                precio_ing = st.number_input("Precio por unidad ($) *", min_value=0.0, value=0.0, step=0.01, format="%.4f")
                stock_ing = st.number_input("Stock inicial *", min_value=0.0, value=0.0, step=1.0)

            submitted_ing = st.form_submit_button("Guardar ingrediente", type="primary")

        if submitted_ing:
            errores = []
            if not nombre_ing.strip():
                errores.append("El nombre no puede estar vacío.")
            if not unidad_ing.strip():
                errores.append("La unidad de medida no puede estar vacía.")
            if precio_ing < 0:
                errores.append("El precio no puede ser negativo.")
            if stock_ing < 0:
                errores.append("El stock no puede ser negativo.")

            if errores:
                for e in errores:
                    st.error(e)
            else:
                db.crear_ingrediente(nombre_ing.strip(), unidad_ing.strip(), precio_ing, stock_ing)
                _show_success(f"Ingrediente '{nombre_ing.strip()}' creado correctamente.")

    # -----------------------------------------------------------------------
    # Tab: Editar ingrediente
    # -----------------------------------------------------------------------
    with tab_editar:
        st.subheader("Editar ingrediente")

        ingredientes_lista = db.listar_ingredientes()
        if not ingredientes_lista:
            st.info("No hay ingredientes para editar.")
        else:
            opciones_ing = {i.nombre: i.id for i in ingredientes_lista}
            sel_ing_ed = st.selectbox("Seleccioná un ingrediente", list(opciones_ing.keys()), key="ed_sel_ing")
            ing_ed = db.obtener_ingrediente(opciones_ing[sel_ing_ed])

            if ing_ed:
                with st.form("form_editar_ing"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nombre_ing_ed = st.text_input("Nombre *", value=ing_ed.nombre)
                        unidad_ing_ed = st.text_input("Unidad *", value=ing_ed.unidad)
                    with col2:
                        precio_ing_ed = st.number_input(
                            "Precio/unidad ($) *",
                            min_value=0.0,
                            value=ing_ed.precio_unitario,
                            step=0.01,
                            format="%.4f",
                        )
                        stock_ing_ed = st.number_input(
                            "Stock *",
                            min_value=0.0,
                            value=ing_ed.stock,
                            step=1.0,
                        )
                    submitted_ing_ed = st.form_submit_button("Guardar cambios", type="primary")

                if submitted_ing_ed:
                    errores = []
                    if not nombre_ing_ed.strip():
                        errores.append("El nombre no puede estar vacío.")
                    if not unidad_ing_ed.strip():
                        errores.append("La unidad no puede estar vacía.")
                    if precio_ing_ed < 0:
                        errores.append("El precio no puede ser negativo.")
                    if stock_ing_ed < 0:
                        errores.append("El stock no puede ser negativo.")

                    if errores:
                        for e in errores:
                            st.error(e)
                    else:
                        ok = db.actualizar_ingrediente(
                            ing_ed.id,
                            nombre_ing_ed.strip(),
                            unidad_ing_ed.strip(),
                            precio_ing_ed,
                            stock_ing_ed,
                        )
                        if ok:
                            _show_success(f"Ingrediente '{nombre_ing_ed.strip()}' actualizado.")
                        else:
                            st.error("No se pudo actualizar el ingrediente.")

    # -----------------------------------------------------------------------
    # Tab: Eliminar ingrediente
    # -----------------------------------------------------------------------
    with tab_eliminar:
        st.subheader("Eliminar ingrediente")

        ingredientes_lista = db.listar_ingredientes()
        if not ingredientes_lista:
            st.info("No hay ingredientes para eliminar.")
        else:
            opciones_del_ing = {i.nombre: i.id for i in ingredientes_lista}
            sel_del_ing = st.selectbox("Seleccioná el ingrediente a eliminar", list(opciones_del_ing.keys()), key="del_ing")
            ing_del = db.obtener_ingrediente(opciones_del_ing[sel_del_ing])

            if ing_del:
                st.warning(
                    f"Estás por eliminar el ingrediente **{ing_del.nombre}** "
                    f"(stock: {ing_del.stock} {ing_del.unidad}). "
                    f"Esta acción no se puede deshacer."
                )
                if st.button("Confirmar eliminación", type="primary", key="btn_del_ing"):
                    ok = db.eliminar_ingrediente(ing_del.id)
                    if ok:
                        _show_success(f"Ingrediente '{ing_del.nombre}' eliminado.")
                    else:
                        st.error("No se pudo eliminar el ingrediente.")

# ===========================================================================
# SECCIÓN: CATEGORÍAS
# ===========================================================================

elif seccion == SEC_CATEGORIAS:
    st.title("Categorías de Cocina")

    tab_lista, tab_nueva, tab_editar, tab_eliminar = st.tabs(
        ["Listado", "Nueva Categoría", "Editar", "Eliminar"]
    )

    # -----------------------------------------------------------------------
    # Tab: Listado
    # -----------------------------------------------------------------------
    with tab_lista:
        st.subheader("Categorías registradas")

        categorias = db.listar_categorias()
        if not categorias:
            st.info("No hay categorías registradas.")
        else:
            for cat in categorias:
                with st.expander(f"🗂️ {cat.nombre}"):
                    st.write(cat.descripcion_completa())
                    recetas_cat = db.listar_recetas(categoria_id=cat.id)
                    if recetas_cat:
                        st.write(f"**Recetas en esta categoría ({len(recetas_cat)}):**")
                        for r in recetas_cat:
                            st.write(f"  • {r.nombre} — {r.tiempo_formateado()} — {r.dificultad}")
                    else:
                        st.caption("Sin recetas asignadas a esta categoría.")

    # -----------------------------------------------------------------------
    # Tab: Nueva categoría
    # -----------------------------------------------------------------------
    with tab_nueva:
        st.subheader("Crear nueva categoría")

        with st.form("form_nueva_cat"):
            nombre_cat = st.text_input("Nombre de la categoría *")
            desc_cat = st.text_area("Descripción")
            submitted_cat = st.form_submit_button("Guardar categoría", type="primary")

        if submitted_cat:
            if not nombre_cat.strip():
                st.error("El nombre de la categoría no puede estar vacío.")
            else:
                db.crear_categoria(nombre_cat.strip(), desc_cat.strip())
                _show_success(f"Categoría '{nombre_cat.strip()}' creada correctamente.")

    # -----------------------------------------------------------------------
    # Tab: Editar categoría
    # -----------------------------------------------------------------------
    with tab_editar:
        st.subheader("Editar categoría")

        categorias = db.listar_categorias()
        if not categorias:
            st.info("No hay categorías para editar.")
        else:
            opciones_cat_ed = {c.nombre: c.id for c in categorias}
            sel_cat_ed = st.selectbox("Seleccioná una categoría", list(opciones_cat_ed.keys()), key="ed_sel_cat")
            cat_ed_obj = db.obtener_categoria(opciones_cat_ed[sel_cat_ed])

            if cat_ed_obj:
                with st.form("form_editar_cat"):
                    nombre_cat_ed = st.text_input("Nombre *", value=cat_ed_obj.nombre)
                    desc_cat_ed = st.text_area("Descripción", value=cat_ed_obj.descripcion)
                    submitted_cat_ed = st.form_submit_button("Guardar cambios", type="primary")

                if submitted_cat_ed:
                    if not nombre_cat_ed.strip():
                        st.error("El nombre no puede estar vacío.")
                    else:
                        ok = db.actualizar_categoria(cat_ed_obj.id, nombre_cat_ed.strip(), desc_cat_ed.strip())
                        if ok:
                            _show_success(f"Categoría '{nombre_cat_ed.strip()}' actualizada.")
                        else:
                            st.error("No se pudo actualizar la categoría.")

    # -----------------------------------------------------------------------
    # Tab: Eliminar categoría
    # -----------------------------------------------------------------------
    with tab_eliminar:
        st.subheader("Eliminar categoría")

        categorias = db.listar_categorias()
        if not categorias:
            st.info("No hay categorías para eliminar.")
        else:
            opciones_del_cat = {c.nombre: c.id for c in categorias}
            sel_del_cat = st.selectbox("Seleccioná la categoría a eliminar", list(opciones_del_cat.keys()), key="del_cat")
            cat_del_obj = db.obtener_categoria(opciones_del_cat[sel_del_cat])

            if cat_del_obj:
                recetas_cat = db.listar_recetas(categoria_id=cat_del_obj.id)
                if recetas_cat:
                    st.warning(
                        f"La categoría **{cat_del_obj.nombre}** tiene "
                        f"{len(recetas_cat)} receta(s) asociada(s). "
                        f"Las recetas quedarán sin categoría si continuás."
                    )
                else:
                    st.warning(
                        f"Estás por eliminar la categoría **{cat_del_obj.nombre}**. "
                        f"Esta acción no se puede deshacer."
                    )
                if st.button("Confirmar eliminación", type="primary", key="btn_del_cat"):
                    ok = db.eliminar_categoria(cat_del_obj.id)
                    if ok:
                        _show_success(f"Categoría '{cat_del_obj.nombre}' eliminada.")
                    else:
                        st.error("No se pudo eliminar la categoría.")

# ===========================================================================
# SECCIÓN: ESTADÍSTICAS
# ===========================================================================

elif seccion == SEC_ESTADISTICAS:
    st.title("Análisis de Datos")

    tab_medidas, tab_importar = st.tabs(["Tendencia Central", "Importar Dataset"])

    # -----------------------------------------------------------------------
    # Tab: Medidas de tendencia central
    # -----------------------------------------------------------------------
    with tab_medidas:
        st.subheader("Medidas de tendencia central")
        st.caption("Variable analizada: tiempo de preparación (minutos)")

        # Los datos se leen directamente de la base con Pandas.
        with db.get_connection() as conn:
            df_recetas = pd.read_sql_query(
                "SELECT nombre, tiempo_preparacion, dificultad FROM recetas", conn
            )

        if df_recetas.empty:
            st.info(
                "Todavía no hay recetas cargadas. "
                "Importá el dataset desde la pestaña de al lado."
            )
        else:
            tiempos = df_recetas["tiempo_preparacion"]

            media = tiempos.mean()
            mediana = tiempos.median()
            moda = tiempos.mode()  # puede traer más de un valor si hay empate

            col1, col2, col3 = st.columns(3)
            col1.metric("Media", f"{media:.2f} min")
            col2.metric("Mediana", f"{mediana:.0f} min")
            col3.metric("Moda", " / ".join(f"{v:.0f} min" for v in moda))

            st.caption(f"Calculado sobre {len(tiempos)} recetas de la base de datos.")

            st.divider()

            st.subheader("Interpretación")
            st.write(_interpretar_tiempos(tiempos))

            moda_dificultad = df_recetas["dificultad"].mode()
            st.caption(
                "Como dato extra, la dificultad más frecuente es "
                f"**{' / '.join(moda_dificultad)}** (moda de una columna no numérica)."
            )

            with st.expander("Ver los datos usados en el cálculo"):
                st.dataframe(df_recetas, use_container_width=True)

    # -----------------------------------------------------------------------
    # Tab: Importar el CSV
    # -----------------------------------------------------------------------
    with tab_importar:
        st.subheader("Importar dataset desde CSV")
        st.write(
            "Lee `datos/recetas.csv` con `pandas.read_csv()` y da de alta cada fila "
            "con la misma función que usa el formulario de Nueva Receta."
        )

        try:
            df_csv = pd.read_csv(importar_datos.CSV_RECETAS)
        except FileNotFoundError:
            df_csv = None
            st.error(f"No se encontró el archivo {importar_datos.CSV_RECETAS}.")

        if df_csv is not None:
            st.caption(
                f"El archivo tiene **{len(df_csv)}** filas "
                f"y {len(df_csv.columns)} columnas."
            )
            st.dataframe(df_csv, use_container_width=True)

            if st.button("Importar a la base de datos", type="primary", key="btn_importar_csv"):
                nuevas, repetidas = importar_datos.importar_recetas_csv()
                if nuevas:
                    _show_success(
                        f"Se importaron {nuevas} receta(s). "
                        f"{repetidas} ya estaban cargadas y se omitieron."
                    )
                else:
                    st.info(
                        f"No se importó ninguna receta nueva: las {repetidas} filas "
                        "del CSV ya están en la base."
                    )
