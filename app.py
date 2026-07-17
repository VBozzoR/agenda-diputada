import streamlit as st
from pyairtable import Api
from datetime import datetime

# --------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA (Forzando visualización limpia)
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Agenda RRSS - Diputada",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------------------------------
# INYECCIÓN DE CONFIGURACIÓN DE TEMA CLARO Y CSS PREMIUM
# Se fuerza el fondo claro, tipografía pulida y tarjetas con sombras (shadows)
# --------------------------------------------------------------------------
st.markdown("""
<style>
    /* Forzar fondo claro en toda la aplicación */
    .stApp {
        background-color: #f8f9fa !important;
        color: #212529 !important;
    }
    
    /* Contenedor principal de la página */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
        max-width: 680px;
    }
    
    /* Títulos y fuentes más institucionales */
    h1, h2, h3, h4, h5, p, span, label {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        color: #1e293b !important;
    }
    
    /* Tarjetas de posts con diseño sofisticado (sombras suaves) */
    .post-card {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 18px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
    }
    
    /* Forzar visibilidad del texto de los guiones y áreas de texto (Copy) */
    .stTextArea textarea {
        color: #1e293b !important;
        background-color: #ffffff !important;
        -webkit-text-fill-color: #1e293b !important; /* Necesario para iOS/Safari móviles */
    }
    
    /* Estilos para áreas de texto deshabilitadas (las de lectura) */
    .stTextArea div[data-baseweb="textarea"] {
        background-color: #f1f5f9 !important;
        border: 1px solid #cbd5e1 !important;
    }
    
    /* Botones más estilizados, planos y modernos */
    .stButton button {
        width: 100%;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        color: #334155 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton button:hover {
        background-color: #f1f5f9 !important;
        border-color: #94a3b8 !important;
    }
    
    /* Estilo especial para los botones del semáforo */
    div.btn-semaforo button {
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        padding: 0 !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
    }
    
    /* Botón de guardar en el Creador Express (Formulario) y botones de acción principal */
    button[data-testid="stFormSubmitButton"] {
        background-color: #1e293b !important;
        border: none !important;
        border-radius: 8px !important;
    }

    button[data-testid="stFormSubmitButton"] p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    button[data-testid="stFormSubmitButton"]:hover {
        background-color: #0f172a !important;
    }
    
    /* Pestañas estilizadas */
    button[data-baseweb="tab"] {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        color: #64748b !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #1e293b !important;
        border-bottom-color: #1e293b !important;
    }

    /* SOLUCIÓN AL OVERLAP DEL EXPANDER: Oculta el bug de texto "arrow_right" o "keyboard_arrow_down" */
    span[data-testid="stIconMaterial"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# CONEXIÓN A AIRTABLE CON CACHÉ ULTRA-RÁPIDA (Optimización de apertura)
# --------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_table():
    api = Api(st.secrets["AIRTABLE_API_KEY"])
    table = api.table(st.secrets["BASE_ID"], st.secrets["TABLE_NAME"])
    return table


@st.cache_data(ttl=900, show_spinner=False)
def obtener_registros_cached():
    table = get_table()
    return table.all()


def cargar_posts(forzar_recarga=False):
    try:
        if forzar_recarga:
            st.cache_data.clear()
            
        registros = obtener_registros_cached()
        st.session_state["posts"] = registros
        st.session_state["conexion_exitosa"] = True
    except Exception as e:
        st.session_state["conexion_exitosa"] = False
        st.session_state["error_mensaje"] = str(e)
        st.session_state["posts"] = []
    st.session_state["last_fetch"] = datetime.now()


if "posts" not in st.session_state:
    cargar_posts(forzar_recarga=False)

# --------------------------------------------------------------------------
# CONSTANTES Y TRADUCCIÓN DE FECHA
# --------------------------------------------------------------------------
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
FORMATOS = ["Reel", "Post (Carrusel)", "Post (Tweet)", "Otro", "Nada"]
TIPOS = ["Contingencia", "Trabajo Territorial", "Agenda Legislativa", "Personal/Blando", "Otro"]
ESTADOS = ["Borrador", "Listo para Aprobación", "Aprobado", "Publicado", "Pausado por Contingencia"]

COLOR_ESTADO = {
    "Borrador": "#64748b",
    "Listo para Aprobación": "#ea580c",
    "Aprobado": "#16a34a",
    "Publicado": "#2563eb",
    "Pausado por Contingencia": "#dc2626",
}

DIAS_TRADUCCION = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}
MESES_TRADUCCION = {
    "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
    "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
    "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

ahora = datetime.now()
dia_semana_ing = ahora.strftime("%A")
mes_ing = ahora.strftime("%B")
dia_semana_esp = DIAS_TRADUCCION.get(dia_semana_ing, dia_semana_ing)
mes_esp = MESES_TRADUCCION.get(mes_ing, mes_ing)
fecha_actual_texto = f"Hoy es {dia_semana_esp}, {ahora.day} de {mes_esp} de {ahora.year}"

# Inicializar el día seleccionado por defecto al día de hoy si no existe
if "dia_seleccionado" not in st.session_state:
    st.session_state["dia_seleccionado"] = dia_semana_esp

# --------------------------------------------------------------------------
# HELPERS DE AIRTABLE
# --------------------------------------------------------------------------
def actualizar_registro(record_id, fields_dict):
    table = get_table()
    try:
        table.update(record_id, fields_dict)
        for r in st.session_state["posts"]:
            if r["id"] == record_id:
                for key, val in fields_dict.items():
                    r["fields"][key] = val
        return True
    except Exception as e:
        st.error(f"No se pudo actualizar en Airtable: {e}")
        return False


def crear_post(fields_dict):
    table = get_table()
    try:
        nuevo = table.create(fields_dict)
        st.session_state["posts"].append(nuevo)
        return True
    except Exception as e:
        st.error(f"No se pudo crear el post: {e}")
        return False


def eliminar_registro(record_id):
    table = get_table()
    try:
        table.delete(record_id)
        st.session_state["posts"] = [r for r in st.session_state["posts"] if r["id"] != record_id]
        return True
    except Exception as e:
        st.error(f"No se pudo eliminar en Airtable: {e}")
        return False


def limpiar_toda_la_semana():
    table = get_table()
    posts_actuales = st.session_state.get("posts", [])
    exito = True
    for post in posts_actuales:
        try:
            table.delete(post["id"])
        except Exception as e:
            exito = False
            st.error(f"Error al eliminar registro {post['id']}: {e}")
            
    if exito:
        st.session_state["posts"] = []
        return True
    return False

# --------------------------------------------------------------------------
# HEADER Y FECHA ACTUAL
# --------------------------------------------------------------------------
st.markdown("### Agenda RRSS")
st.markdown(f"<p style='color: #64748b; font-size: 0.9rem; margin-top: -10px;'>{fecha_actual_texto}</p>", unsafe_allow_html=True)

if "conexion_exitosa" in st.session_state and not st.session_state["conexion_exitosa"]:
    st.error(f"Error de conexión con Airtable: {st.session_state.get('error_mensaje', 'Desconocido')}")

# --------------------------------------------------------------------------
# SECCIÓN "HOY" DESTACADA (Arriba de todo)
# --------------------------------------------------------------------------
posts = st.session_state.get("posts", [])
posts_hoy = [p for p in posts if p["fields"].get("Dia") == dia_semana_esp]

with st.container():
    st.markdown(f"#### Hoy ({dia_semana_esp})")
    if not posts_hoy:
        st.caption("No hay publicaciones planificadas para hoy.")
    else:
        for post_hoy in posts_hoy:
            f_hoy = post_hoy["fields"]
            record_id_hoy = post_hoy["id"]
            estado_actual_hoy = f_hoy.get("Estado", "Borrador")
            color_hoy = COLOR_ESTADO.get(estado_actual_hoy, "#9E9E9E")

            st.markdown(f"""
            <div class="post-card" style="border-left: 4px solid {color_hoy} !important;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; color: #64748b;">
                        {f_hoy.get('Formato', '—')} &nbsp;·&nbsp; {f_hoy.get('Tipo', '—')}
                    </span>
                    <span style="background-color: {color_hoy}; color: white; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">
                        {estado_actual_hoy}
                    </span>
                </div>
                <h4 style="margin: 0 0 10px 0; font-size: 1.1rem; font-weight: 700; color: #1e293b;">
                    {f_hoy.get('Titulo', 'Sin Título')}
                </h4>
            </div>
            """, unsafe_allow_html=True)

            copy_hoy = f_hoy.get("Copy", "")
            if copy_hoy:
                st.text_area("Texto Copy Hoy", value=copy_hoy, height=100, disabled=True, key=f"text_area_hoy_{record_id_hoy}", label_visibility="collapsed")
                
                js_copy_code_hoy = f"""
                <script>
                function copiarTextoHoy_{record_id_hoy}() {{
                    var dummy = document.createElement("textarea");
                    document.body.appendChild(dummy);
                    dummy.value = `{copy_hoy.replace('`', '\\`').replace('$', '\\$')}`;
                    dummy.select();
                    document.execCommand("copy");
                    document.body.removeChild(dummy);
                    alert("¡Copy copiado al portapapeles con éxito!");
                }}
                </script>
                <button onclick="copiarTextoHoy_{record_id_hoy}()" style="
                    width: 100%;
                    background-color: #1e293b;
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 0.85rem;
                    cursor: pointer;
                    margin-bottom: 12px;
                ">Copiar Copy</button>
                """
                st.components.v1.html(js_copy_code_hoy, height=45)

            if f_hoy.get("Multimedia_Link"):
                st.markdown(f"<p style='font-size: 0.85rem; color: #475569;'><strong>Apoyo visual:</strong> {f_hoy['Multimedia_Link']}</p>", unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 15px; margin-bottom: 15px; border: 0; border-top: 1px solid #cbd5e1;'>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# NUEVO: SEMÁFORO SEMANAL INTERACTIVO (Botonera de Navegación por Día)
# --------------------------------------------------------------------------
st.markdown("<p style='font-weight: 700; font-size: 0.9rem; margin-bottom: 8px; text-align: center; color: #475569;'>Planificación de la Semana</p>", unsafe_allow_html=True)

iniciales_dias = {"Lunes": "L", "Martes": "M", "Miércoles": "M", "Jueves": "J", "Viernes": "V", "Sábado": "S", "Domingo": "D"}

# Dibujamos los 7 botones del semáforo lado a lado
cols_semaforo = st.columns(7)
for i, dia in enumerate(DIAS):
    with cols_semaforo[i]:
        tiene_contenido = any(p["fields"].get("Dia") == dia for p in posts)
        
        # Lógica de colores dinámicos (Fondos sólidos)
        if st.session_state["dia_seleccionado"] == dia:
            # SI ESTÁ SELECCIONADO: Fondo azul oscuro y letra blanca
            estilo_css = f"""
            <style>
                div[data-testid="stHorizontalBlock"] > div:nth-child({i+1}) button {{
                    background-color: #1e293b !important;
                    border-color: #1e293b !important;
                }}
                div[data-testid="stHorizontalBlock"] > div:nth-child({i+1}) button p {{
                    color: #ffffff !important;
                }}
            </style>
            """
            st.markdown(estilo_css, unsafe_allow_html=True)
        elif tiene_contenido:
            # SI TIENE CONTENIDO (Y no está seleccionado): Fondo verde esmeralda y letra blanca
            estilo_css = f"""
            <style>
                div[data-testid="stHorizontalBlock"] > div:nth-child({i+1}) button {{
                    background-color: #16a34a !important;
                    border-color: #16a34a !important;
                }}
                div[data-testid="stHorizontalBlock"] > div:nth-child({i+1}) button p {{
                    color: #ffffff !important;
                }}
            </style>
            """
            st.markdown(estilo_css, unsafe_allow_html=True)
        else:
            # SI ESTÁ VACÍO: Mantiene el diseño limpio original (Fondo blanco, borde sutil y letra gris)
            estilo_css = f"""
            <style>
                div[data-testid="stHorizontalBlock"] > div:nth-child({i+1}) button {{
                    background-color: #ffffff !important;
                    border-color: #cbd5e1 !important;
                }}
                div[data-testid="stHorizontalBlock"] > div:nth-child({i+1}) button p {{
                    color: #94a3b8 !important;
                }}
            </style>
            """
            st.markdown(estilo_css, unsafe_allow_html=True)
            
        st.markdown('<div class="btn-semaforo">', unsafe_allow_html=True)
        if st.button(iniciales_dias[dia], key=f"btn_nav_{dia}"):
            st.session_state["dia_seleccionado"] = dia
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.write("")

col_a, col_b = st.columns([3, 1])
with col_a:
    st.caption(f"Visualizando: **{st.session_state['dia_seleccionado']}** (Toca una letra para cambiar)")
with col_b:
    if st.button("Actualizar", use_container_width=True):
        cargar_posts(forzar_recarga=True)
        st.rerun()

# --------------------------------------------------------------------------
# CÁLCULO DE ALERTAS PARA "MODO DIPUTADA"
# --------------------------------------------------------------------------
pendientes = [p for p in posts if p["fields"].get("Estado") == "Listo para Aprobación"]
num_pendientes = len(pendientes)
nombre_tab_diputada = f"Modo Diputada ({num_pendientes})" if num_pendientes > 0 else "Modo Diputada"

tab1, tab2, tab3 = st.tabs(["Agenda Semanal", "Creador Express", nombre_tab_diputada])

# ============================================================================
# PESTAÑA 1: AGENDA SEMANAL
# ============================================================================
with tab1:
    # Usamos el día del estado interno del semáforo
    dia_actual_agenda = st.session_state["dia_seleccionado"]
    st.markdown(f"#### Planificación: {dia_actual_agenda}")

    # Módulo de Limpieza de Semana Completa
    if posts:
        with st.expander("Herramientas de Administración"):
            st.write("Esta acción eliminará todos los posts planificados de forma definitiva para iniciar una nueva semana.")
            if st.button("Limpiar Semana Completa", key="btn_limpiar_semana"):
                st.session_state["confirmar_limpieza_global"] = True
                
            if st.session_state.get("confirmar_limpieza_global", False):
                st.warning("¿Estás completamente seguro? Esta acción no se puede deshacer.")
                col_clear_si, col_clear_no = st.columns(2)
                with col_clear_si:
                    if st.button("Sí, Limpiar Todo", key="confirm_clear_si"):
                        if limpiar_toda_la_semana():
                            st.session_state["confirmar_limpieza_global"] = False
                            st.toast("La agenda semanal ha sido reiniciada por completo")
                            st.rerun()
                with col_clear_no:
                    if st.button("No, Cancelar", key="confirm_clear_no"):
                        st.session_state["confirmar_limpieza_global"] = False
                        st.rerun()

    posts_dia = [p for p in posts if p["fields"].get("Dia") == dia_actual_agenda]

    if not posts_dia:
        st.info(f"No hay publicaciones agendadas para el {dia_actual_agenda}.")
    else:
        for post in posts_dia:
            f = post["fields"]
            record_id = post["id"]
            estado_actual = f.get("Estado", "Borrador")
            color = COLOR_ESTADO.get(estado_actual, "#9E9E9E")

            st.markdown(f"""
            <div class="post-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; color: #64748b;">
                        {f.get('Formato', '—')} &nbsp;·&nbsp; {f.get('Tipo', '—')}
                    </span>
                    <span style="background-color: {color}; color: white; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">
                        {estado_actual}
                    </span>
                </div>
                <h4 style="margin: 0 0 10px 0; font-size: 1.1rem; font-weight: 700; color: #1e293b;">
                    {f.get('Titulo', 'Sin Título')}
                </h4>
            </div>
            """, unsafe_allow_html=True)

            with st.container():
                copy_texto = f.get("Copy", "")
                if copy_texto:
                    st.text_area("Texto Copy", value=copy_texto, height=120, disabled=True, key=f"text_area_{record_id}", label_visibility="collapsed")
                    
                    js_copy_code = f"""
                    <script>
                    function copiarTexto_{record_id}() {{
                        var dummy = document.createElement("textarea");
                        document.body.appendChild(dummy);
                        dummy.value = `{copy_texto.replace('`', '\\`').replace('$', '\\$')}`;
                        dummy.select();
                        document.execCommand("copy");
                        document.body.removeChild(dummy);
                        alert("¡Copy copiado al portapapeles con éxito!");
                    }}
                    </script>
                    <button onclick="copiarTexto_{record_id}()" style="
                        width: 100%;
                        background-color: #1e293b;
                        color: white;
                        border: none;
                        padding: 8px 12px;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 0.85rem;
                        cursor: pointer;
                        margin-bottom: 12px;
                    ">Copiar Copy</button>
                    """
                    st.components.v1.html(js_copy_code, height=45)

                if f.get("Multimedia_Link"):
                    st.markdown(f"<p style='font-size: 0.85rem; margin-top: -5px; color: #475569;'><strong>Apoyo visual:</strong> {f['Multimedia_Link']}</p>", unsafe_allow_html=True)

                st.write("") 

                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                
                with col_btn1:
                    if st.button("Editar", key=f"edit_btn_{record_id}"):
                        st.session_state[f"editando_{record_id}"] = True

                with col_btn2:
                    if estado_actual != "Pausado por Contingencia":
                        if st.button("Pausar", key=f"pausa_{record_id}"):
                            if actualizar_registro(record_id, {"Estado": "Pausado por Contingencia"}):
                                st.toast("Post pausado por contingencia")
                                st.rerun()
                    else:
                        st.caption("Pausado")

                with col_btn3:
                    if st.button("Eliminar", key=f"confirm_del_{record_id}"):
                        st.session_state[f"confirmar_eliminar_{record_id}"] = True

                if st.session_state.get(f"editando_{record_id}", False):
                    with st.form(f"form_editar_{record_id}"):
                        st.write("**Editar Publicación**")
                        nuevo_titulo = st.text_input("Título", value=f.get("Titulo", ""))
                        nuevo_dia = st.selectbox("Día", DIAS, index=DIAS.index(f.get("Dia", "Lunes")))
                        nuevo_formato = st.selectbox("Formato", FORMATOS, index=FORMATOS.index(f.get("Formato", "Reel")))
                        nuevo_tipo = st.selectbox("Tipo de Contenido", TIPOS, index=TIPOS.index(f.get("Tipo", "Contingencia")))
                        nuevo_copy = st.text_area("Copy / Guion", value=copy_texto)
                        nuevo_visual = st.text_input("Idea de Apoyo Visual", value=f.get("Multimedia_Link", ""))
                        nuevo_est = st.selectbox("Estado", ESTADOS, index=ESTADOS.index(estado_actual))
                        
                        col_form_btn1, col_form_btn2 = st.columns(2)
                        with col_form_btn1:
                            guardar = st.form_submit_button("Guardar Cambios")
                        with col_form_btn2:
                            cancelar = st.form_submit_button("Cancelar")

                        if guardar:
                            campos_nuevos = {
                                "Titulo": nuevo_titulo,
                                "Dia": nuevo_dia,
                                "Formato": nuevo_formato,
                                "Tipo": nuevo_tipo,
                                "Copy": nuevo_copy,
                                "Multimedia_Link": nuevo_visual,
                                "Estado": nuevo_est
                            }
                            if actualizar_registro(record_id, campos_nuevos):
                                st.session_state[f"editando_{record_id}"] = False
                                st.toast("Cambios guardados")
                                st.rerun()
                        if cancelar:
                            st.session_state[f"editando_{record_id}"] = False
                            st.rerun()

                if st.session_state.get(f"confirmar_eliminar_{record_id}", False):
                    st.warning("¿Estás seguro de que deseas eliminar este post de forma definitiva?")
                    col_del_si, col_del_no = st.columns(2)
                    with col_del_si:
                        if st.button("Sí, Eliminar", key=f"del_si_{record_id}"):
                            if eliminar_registro(record_id):
                                st.session_state[f"confirmar_eliminar_{record_id}"] = False
                                st.toast("Post eliminado con éxito")
                                st.rerun()
                    with col_del_no:
                        if st.button("No, Cancelar", key=f"del_no_{record_id}"):
                            st.session_state[f"confirmar_eliminar_{record_id}"] = False
                            st.rerun()
            st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px; border: 0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

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
            placeholder="Escribe aquí el borrador del copy...",
        )

        visual_sel = st.text_input(
            "Idea de Apoyo Visual",
            placeholder="Ej: Foto de la sesión de sala o Video de apoyo territorial",
        )

        estado_sel = st.selectbox(
            "Estado inicial",
            ["Borrador", "Listo para Aprobación"],
            index=0,
        )

        enviado = st.form_submit_button("Guardar Post", use_container_width=True)

        if enviado:
            if formato_sel == "Nada":
                nuevo_registro = {
                    "Titulo": titulo if titulo.strip() else "Día sin contenido",
                    "Dia": dia_sel,
                    "Formato": formato_sel,
                    "Tipo": tipo_sel,
                    "Copy": copy_sel if copy_sel.strip() else "Día planificado libre de publicaciones.",
                    "Estado": "Borrador",
                    "Multimedia_Link": visual_sel,
                }
                if crear_post(nuevo_registro):
                    st.success("Día sin contenido registrado.")
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
                    "Multimedia_Link": visual_sel,
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

    if not pendientes:
        st.success("No hay posts pendientes de aprobación. Todo al día.")

    for post in pendientes:
        f = post["fields"]
        record_id = post["id"]

        with st.container():
            st.markdown(f"""
            <div class="post-card" style="border-left: 4px solid #ea580c !important;">
                <span style="font-size: 0.8rem; text-transform: uppercase; font-weight: 700; color: #64748b;">
                    {f.get('Dia', '—')} &nbsp;·&nbsp; {f.get('Formato', '—')} &nbsp;·&nbsp; {f.get('Tipo', '—')}
                </span>
                <h4 style="margin: 5px 0 10px 0; font-size: 1.1rem; font-weight: 700;">
                    {f.get('Titulo', 'Sin Título')}
                </h4>
                <p style="background-color: #f8f9fa; padding: 12px; border-radius: 6px; font-size: 0.95rem; line-height: 1.4; border-left: 2px solid #cbd5e1;">
                    {f.get('Copy', '(sin copy)')}
                </p>
            </div>
            """, unsafe_allow_html=True)

            if f.get("Multimedia_Link"):
                st.markdown(f"<p style='font-size: 0.85rem; margin-top: -5px; color: #475569;'><strong>Apoyo visual:</strong> {f['Multimedia_Link']}</p>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Aprobar", key=f"aprobar_{record_id}", use_container_width=True):
                    if actualizar_registro(record_id, {"Estado": "Aprobado"}):
                        st.toast("Post aprobado")
                        st.rerun()
            with col2:
                if st.button("Corregir", key=f"corregir_btn_{record_id}", use_container_width=True):
                    st.session_state[f"mostrar_correccion_{record_id}"] = True

            if st.session_state.get(f"mostrar_correccion_{record_id}", False):
                comentario = st.text_area(
                    "Comentarios de corrección",
                    key=f"comentario_{record_id}",
                    placeholder="Ej: cambiar el título, agregar cifra X...",
                )
                if st.button(
                    "Guardar corrección y devolver a Borrador",
                    key=f"guardar_correccion_{record_id}",
                    use_container_width=True,
                ):
                    if comentario.strip():
                        copy_original = f.get("Copy", "")
                        nuevo_copy = f"[CORRECCIÓN DIPUTADA: {comentario.strip()}]\n\n{copy_original}"
                        if actualizar_registro(record_id, {"Estado": "Borrador", "Copy": nuevo_copy}):
                            st.session_state[f"mostrar_correccion_{record_id}"] = False
                            st.toast("Comentarios guardados")
                            st.rerun()
                    else:
                        st.warning("Escribe un comentario antes de guardar.")
            st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px; border: 0; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# FOOTER
# --------------------------------------------------------------------------
st.write("")
st.caption(
    f"Última sincronización: "
    f"{st.session_state.get('last_fetch', datetime.now()).strftime('%d-%m-%Y %H:%M:%S')}"
)
