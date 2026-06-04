"""
Chef Master Pro – Aplicación principal de Streamlit.
Sistema de Gestión del Instituto ORT Cuisine.
"""

import streamlit as st
from streamlit_option_menu import option_menu

import database as db
from models import Receta, Ingrediente, Categoria

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Chef Master Pro",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializar la base de datos (crea tablas e inserta datos de ejemplo si es necesario)
db.init_db()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DIFICULTADES = ["Baja", "Media", "Alta"]


def _badge_dificultad(dificultad: str) -> str:
    colores = {"Baja": "🟢", "Media": "🟡", "Alta": "🔴"}
    return colores.get(dificultad, "⚪") + " " + dificultad


def _show_success(msg: str) -> None:
    st.success(msg)
    st.rerun()


# ---------------------------------------------------------------------------
# Sidebar – Navegación
# ---------------------------------------------------------------------------

from streamlit_option_menu import option_menu

st.sidebar.title("Chef Master Pro")
st.sidebar.caption("Instituto ORT Cuisine")
st.sidebar.divider()

with st.sidebar:
    seccion = option_menu(
        menu_title="Menú principal",
        options=["Recetas", "Ingredientes", "Categorías"],
        icons=["journal-text", "basket", "tags"],
        menu_icon="list",
        default_index=0,
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "transparent"
            },
            "icon": {
                "font-size": "15px"
            },
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#eee",
            },
            "nav-link-selected": {
                "background-color": "#5856D6",
            },
        }
    )

st.sidebar.divider()
st.sidebar.info("Sistema de Gestión Gastronómica\n\nInstituto ORT Cuisine © 2026")

# ===========================================================================
# SECCIÓN: RECETAS
# ===========================================================================

if seccion == "Recetas":
    st.title("📋 Gestión de Recetas")

    tab_lista, tab_nueva, tab_editar, tab_eliminar = st.tabs(
        ["📄 Listado", "➕ Nueva Receta", "✏️ Editar", "🗑️ Eliminar"]
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
                        st.metric("⏱️ Tiempo", receta.tiempo_formateado())
                        st.write(_badge_dificultad(receta.dificultad))
                        if receta.es_compleja():
                            st.caption("⚠️ Receta compleja")

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

            submitted = st.form_submit_button("✅ Guardar receta", type="primary")

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
                _show_success(f"✅ Receta '{nombre.strip()}' creada correctamente.")

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

                    submitted_ed = st.form_submit_button("💾 Guardar cambios", type="primary")

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
                            _show_success(f"✅ Receta '{nombre_ed.strip()}' actualizada correctamente.")
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
                    f"⚠️ Estás por eliminar **{receta_del.nombre}** "
                    f"(categoría: {receta_del.categoria_nombre or '—'}). "
                    f"Esta acción no se puede deshacer."
                )
                if st.button("🗑️ Confirmar eliminación", type="primary", key="btn_del_receta"):
                    ok = db.eliminar_receta(receta_del.id)
                    if ok:
                        _show_success(f"✅ Receta '{receta_del.nombre}' eliminada.")
                    else:
                        st.error("No se pudo eliminar la receta.")

# ===========================================================================
# SECCIÓN: INGREDIENTES
# ===========================================================================

elif seccion == "Ingredientes":
    st.title("🥦 Inventario de Ingredientes")

    tab_lista, tab_nuevo, tab_editar, tab_eliminar = st.tabs(
        ["📄 Listado", "➕ Nuevo Ingrediente", "✏️ Editar", "🗑️ Eliminar"]
    )

    # -----------------------------------------------------------------------
    # Tab: Listado con filtros
    # -----------------------------------------------------------------------
    with tab_lista:
        st.subheader("Inventario actual")

        col1, col2 = st.columns(2)
        with col1:
            busqueda = st.text_input("🔍 Buscar por nombre", key="busq_ing")
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
                    "Disponible": "✅" if ing.es_disponible(0.01) else "❌",
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

            submitted_ing = st.form_submit_button("✅ Guardar ingrediente", type="primary")

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
                _show_success(f"✅ Ingrediente '{nombre_ing.strip()}' creado correctamente.")

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
                    submitted_ing_ed = st.form_submit_button("💾 Guardar cambios", type="primary")

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
                            _show_success(f"✅ Ingrediente '{nombre_ing_ed.strip()}' actualizado.")
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
                    f"⚠️ Estás por eliminar el ingrediente **{ing_del.nombre}** "
                    f"(stock: {ing_del.stock} {ing_del.unidad}). "
                    f"Esta acción no se puede deshacer."
                )
                if st.button("🗑️ Confirmar eliminación", type="primary", key="btn_del_ing"):
                    ok = db.eliminar_ingrediente(ing_del.id)
                    if ok:
                        _show_success(f"✅ Ingrediente '{ing_del.nombre}' eliminado.")
                    else:
                        st.error("No se pudo eliminar el ingrediente.")

# ===========================================================================
# SECCIÓN: CATEGORÍAS
# ===========================================================================

elif seccion == "Categorías":
    st.title("🗂️ Categorías de Cocina")

    tab_lista, tab_nueva, tab_editar, tab_eliminar = st.tabs(
        ["📄 Listado", "➕ Nueva Categoría", "✏️ Editar", "🗑️ Eliminar"]
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
                            st.write(f"  • {r.nombre} — {r.tiempo_formateado()} — {_badge_dificultad(r.dificultad)}")
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
            submitted_cat = st.form_submit_button("✅ Guardar categoría", type="primary")

        if submitted_cat:
            if not nombre_cat.strip():
                st.error("El nombre de la categoría no puede estar vacío.")
            else:
                db.crear_categoria(nombre_cat.strip(), desc_cat.strip())
                _show_success(f"✅ Categoría '{nombre_cat.strip()}' creada correctamente.")

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
                    submitted_cat_ed = st.form_submit_button("💾 Guardar cambios", type="primary")

                if submitted_cat_ed:
                    if not nombre_cat_ed.strip():
                        st.error("El nombre no puede estar vacío.")
                    else:
                        ok = db.actualizar_categoria(cat_ed_obj.id, nombre_cat_ed.strip(), desc_cat_ed.strip())
                        if ok:
                            _show_success(f"✅ Categoría '{nombre_cat_ed.strip()}' actualizada.")
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
                        f"⚠️ La categoría **{cat_del_obj.nombre}** tiene "
                        f"{len(recetas_cat)} receta(s) asociada(s). "
                        f"Las recetas quedarán sin categoría si continuás."
                    )
                else:
                    st.warning(
                        f"⚠️ Estás por eliminar la categoría **{cat_del_obj.nombre}**. "
                        f"Esta acción no se puede deshacer."
                    )
                if st.button("🗑️ Confirmar eliminación", type="primary", key="btn_del_cat"):
                    ok = db.eliminar_categoria(cat_del_obj.id)
                    if ok:
                        _show_success(f"✅ Categoría '{cat_del_obj.nombre}' eliminada.")
                    else:
                        st.error("No se pudo eliminar la categoría.")
