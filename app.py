import streamlit as st
from pyairtable import Api
from datetime import datetime

# --------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Agenda RRSS - Diputada",
    page_icon="🏛️",
    layout="centered",           # 'centered' se ve mucho mejor en celular que 'wide'
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------------------------------
# CSS PERSONALIZADO -> hace que la app se vea como una app móvil real
# --------------------------------------------------------------------------
st.markdown("""
<style>
    /* Reduce paddings para aprovechar pantallas chicas */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 720px;
    }
    /* Tarjetas */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px !important;
    }
    /* Botones más grandes y táctiles */
    .stButton button {
        width: 100%;
        border-radius: 10px;
        padding: 0.55rem 0.75rem;
        font-weight: 600;
    }
    /* Tabs más compactos */
    button[data-baseweb="tab"] {
        font-size: 0.95rem;
        font-weight: 600;
    }
    h1, h2, h3 { line-height: 1.25; }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# CONEXIÓN A AIRTABLE
# --------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_table():
    """Crea (y cachea) la conexión a la tabla de Airtable."""
    api = Api(st.secrets["AIRTABLE_API_KEY"])
    table = api.table(st.secrets["BASE_ID"], st.secrets["TABLE_NAME"])
    return table


def cargar_posts():
    """Trae los registros de Airtable con un sistema de seguridad para no congelarse."""
    try:
        table = get_table()
        registros = table.all() 
        st.session_state["posts"] = registros
        st.session_state["conexion_exitosa"] = True
    except Exception as e:
        st.session_state["conexion_exitosa"] = False
        st.session_state["error_mensaje"] = str(e)
        st.session_state["posts"] = []
    st.session_state["last_fetch"] = datetime.now()


if "posts" not in st.session_state:
    cargar_posts()

# --------------------------------------------------------------------------
# CONSTANTES / OPCIONES (deben calzar EXACTO con los Single Select de Airtable)
# --------------------------------------------------------------------------
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
FORMATOS = ["Reel", "Post (Carrusel)", "Post (Tweet)", "Otro", "Nada"]
TIPOS = ["Contingencia", "Trabajo Territorial", "Agenda Legislativa", "Personal/Blando", "Otro"]
ESTADOS = ["Borrador", "Listo para Aprobación", "Aprobado", "Publicado", "Pausado por Contingencia"]

# Colores por Estado, para dar contexto visual inmediato
COLOR_ESTADO = {
    "Borrador": "#9E9E9E",
    "Listo para Aprobación": "#FF9800",
    "Aprobado": "#4CAF50",
    "Publicado": "#2196F3",
    "Pausado por Contingencia": "#E53935",
}

# --------------------------------------------------------------------------
# HELPERS DE ACTUALIZACIÓN (Airtable + refresco de session_state)
# --------------------------------------------------------------------------
def actualizar_estado(record_id, nuevo_estado, nuevo_copy=None):
    """Actualiza el Estado (y opcionalmente el Copy) de un registro en Airtable."""
    table = get_table()
    fields = {"Estado": nuevo_estado}
    if nuevo_copy is not None:
        fields["Copy"] = nuevo_copy
    try:
        table.update(record_id, fields)
        # Actualiza también la copia local en session_state para respuesta instantánea
        for r in st.session_state["posts"]:
            if r["id"] == record_id:
                r["fields"]["Estado"] = nuevo_estado
                if nuevo_copy is not None:
                    r["fields"]["Copy"] = nuevo_copy
        return True
    except Exception as e:
        st.error(f"No se pudo actualizar: {e}")
        return False


def crear_post(fields_dict):
    """Crea un nuevo registro en Airtable."""
    table = get_table()
    try:
        nuevo = table.create(fields_dict)
        st.session_state["posts"].append(nuevo)
        return True
    except Exception as e:
        st.error(f"No se pudo crear el post: {e}")
        return False


# --------------------------------------------------------------------------
# HEADER Y CONTROL DE CONEXIÓN
# --------------------------------------------------------------------------
st.markdown("### Agenda RRSS")

# Alerta de conexión visual si Airtable falla
if "conexion_exitosa" in st.session_state and not st.session_state["conexion_exitosa"]:
    st.error(f"Error de conexión con Airtable: {st.session_state.get('error_mensaje', 'Desconocido')}")
    st.info("Asegúrate de que tus credenciales en `.streamlit/secrets.toml` sean correctas.")

col_a, col_b = st.columns([3, 1])
with col_a:
    st.caption("Gestión rápida de contenido para redes sociales")
with col_b:
    if st.button("Actualizar", use_container_width=True):
        cargar_posts()
        st.rerun()

tab1, tab2, tab3 = st.tabs(["Agenda Semanal", "Creador Express", "Modo Diputada"])

# ============================================================================
# PESTAÑA 1: AGENDA SEMANAL
# ============================================================================
with tab1:
    st.markdown("#### Agenda Semanal")

    posts = st.session_state.get("posts", [])

    if not posts:
        st.info("No hay posts cargados todavía. Usa 'Creador Express' para crear el primero.")

    for dia in DIAS:
        posts_dia = [p for p in posts if p["fields"].get("Dia") == dia]
        if not posts_dia:
            continue  # Solo mostramos días que tengan contenido, para no saturar el celular

        st.markdown(f"##### {dia}")

        for post in posts_dia:
            f = post["fields"]
            record_id = post["id"]
            estado_actual = f.get("Estado", "Borrador")
            color = COLOR_ESTADO.get(estado_actual, "#9E9E9E")

            with st.container(border=True):
                # Encabezado de la tarjeta: Formato + Tipo
                st.markdown(
                    f"**{f.get('Formato', '—')}** &nbsp;·&nbsp; {f.get('Tipo', '—')}"
                )
                if f.get("Titulo"):
                    st.markdown(f"**{f.get('Titulo')}**")

                # Copy (borrador de texto)
                copy_texto = f.get("Copy", "")
                if copy_texto:
                    preview = copy_texto if len(copy_texto) <= 180 else copy_texto[:180] + "…"
                    st.caption(preview)

                # Multimedia
                if f.get("Multimedia_Link"):
                    st.markdown(f"[Ver multimedia]({f['Multimedia_Link']})")

                # Badge de estado con color
                st.markdown(
                    f"""<span style="background-color:{color}; color:white;
                    padding:3px 10px; border-radius:20px; font-size:0.75rem;
                    font-weight:600;">{estado_actual}</span>""",
                    unsafe_allow_html=True,
                )

                st.write("")  # pequeño espacio

                # Botón de pausa por contingencia (no se muestra si ya está pausado)
                if estado_actual != "Pausado por Contingencia":
                    if st.button(
                        "Pausar por Contingencia",
                        key=f"pausa_{record_id}",
                        use_container_width=True,
                    ):
                        if actualizar_estado(record_id, "Pausado por Contingencia"):
                            st.toast("Post pausado por contingencia", icon="⏸️")
                            st.rerun()
                else:
                    st.caption("Este post está pausado.")

# ============================================================================
# PESTAÑA 2: CREADOR EXPRESS
# ============================================================================
with tab2:
    st.markdown("#### Creador Express")
    st.caption("Crea un post nuevo en segundos, ideal para responder a la contingencia.")

    with st.form("form_creador_express", clear_on_submit=True):
        titulo = st.text_input("Título / referencia interna", placeholder="Ej: Reel vocería MEPCO")

        dia_sel = st.selectbox("Día", DIAS)
        formato_sel = st.selectbox("Formato", FORMATOS)
        tipo_sel = st.selectbox("Tipo de Contenido", TIPOS)

        copy_sel = st.text_area(
            "Copy / Guion",
            height=180,
            placeholder="Escribe aquí el borrador del copy o guion del post...",
        )

        multimedia_sel = st.text_input(
            "Link Multimedia (Drive, etc.)",
            placeholder="https://drive.google.com/...",
        )

        estado_sel = st.selectbox(
            "Estado inicial",
            ["Borrador", "Listo para Aprobación"],
            index=0,
        )

        enviado = st.form_submit_button("Guardar Post", use_container_width=True)

        if enviado:
            # Permitimos guardar sin copy si el formato es "Nada" (día libre de contenido)
            if formato_sel == "Nada":
                nuevo_registro = {
                    "Titulo": titulo if titulo.strip() else "Día sin contenido",
                    "Dia": dia_sel,
                    "Formato": formato_sel,
                    "Tipo": tipo_sel,
                    "Copy": copy_sel if copy_sel.strip() else "Día planificado libre de publicaciones.",
                    "Estado": "Borrador",
                    "Multimedia_Link": multimedia_sel,
                }
                if crear_post(nuevo_registro):
                    st.success("Día sin contenido registrado en la planificación.")
                    st.rerun()
            elif not copy_sel.strip():
                st.warning("Escribe al menos un borrador de Copy antes de guardar.")
            else:
                nuevo_registro = {
                    "Titulo": titulo,
                    "Dia": dia_sel,
                    "Formato": formato_sel,
                    "Tipo": tipo_sel,
                    "Copy": copy_sel,
                    "Estado": estado_sel,
                    "Multimedia_Link": multimedia_sel,
                }
                if crear_post(nuevo_registro):
                    st.success("Post creado y guardado en Airtable.")
                    st.rerun()

# ============================================================================
# PESTAÑA 3: MODO DIPUTADA (APROBACIONES)
# ============================================================================
with tab3:
    st.markdown("#### Modo Diputada")
    st.caption("Solo lo esencial: revisa y aprueba con un toque.")

    posts = st.session_state.get("posts", [])
    pendientes = [p for p in posts if p["fields"].get("Estado") == "Listo para Aprobación"]

    if not pendientes:
        st.success("No hay posts pendientes de aprobación. ¡Todo al día!")

    for post in pendientes:
        f = post["fields"]
        record_id = post["id"]

        with st.container(border=True):
            st.markdown(f"**{f.get('Dia', '—')}** · {f.get('Formato', '—')} · {f.get('Tipo', '—')}")
            if f.get("Titulo"):
                st.markdown(f"*{f.get('Titulo')}*")

            st.markdown(f"> {f.get('Copy', '(sin copy)')}")

            if f.get("Multimedia_Link"):
                st.markdown(f"[Ver multimedia]({f['Multimedia_Link']})")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Aprobar", key=f"aprobar_{record_id}", use_container_width=True):
                    if actualizar_estado(record_id, "Aprobado"):
                        st.toast("Post aprobado", icon="👍")
                        st.rerun()
            with col2:
                if st.button("Corregir", key=f"corregir_btn_{record_id}", use_container_width=True):
                    st.session_state[f"mostrar_correccion_{record_id}"] = True

            # Si se activó "Corregir", mostramos el campo de comentarios
            if st.session_state.get(f"mostrar_correccion_{record_id}", False):
                comentario = st.text_area(
                    "Comentarios de corrección",
                    key=f"comentario_{record_id}",
                    placeholder="Ej: cambiar el título, agregar cifra X, tono más cercano...",
                )
                if st.button(
                    "Guardar corrección y devolver a Borrador",
                    key=f"guardar_correccion_{record_id}",
                    use_container_width=True,
                ):
                    if comentario.strip():
                        copy_original = f.get("Copy", "")
                        nuevo_copy = f"[CORRECCIÓN DIPUTADA: {comentario.strip()}]\n\n{copy_original}"
                        if actualizar_estado(record_id, "Borrador", nuevo_copy=nuevo_copy):
                            st.session_state[f"mostrar_correccion_{record_id}"] = False
                            st.toast("Comentarios guardados, post devuelto a Borrador", icon="📝")
                            st.rerun()
                    else:
                        st.warning("Escribe un comentario antes de guardar.")

# --------------------------------------------------------------------------
# FOOTER
# --------------------------------------------------------------------------
st.write("")
st.caption(
    f"Última sincronización: "
    f"{st.session_state.get('last_fetch', datetime.now()).strftime('%d-%m-%Y %H:%M:%S')}"
)