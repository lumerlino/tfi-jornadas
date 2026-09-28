import streamlit as st


# --------------------------------------------------
# Registro de páginas para navegar desde adentro de una vista.
#
# app.py crea las st.Page y las registra acá; las vistas solo
# importan este módulo (no app.py), así no hay imports circulares.
# --------------------------------------------------

PAGINAS = {}


def ir_a(clave, texto, principal=False):

    if st.button(
        texto,
        key=f"ir_a_{clave}",
        type="primary" if principal else "secondary"
    ):
        st.switch_page(PAGINAS[clave])


# --------------------------------------------------
# MENÚ LATERAL
#
# Secciones con rótulo: las tres preguntas ("Analizar") y la
# trastienda ("Datos"). Las tareas de Preparar datos aparecen
# debajo, más chicas, solo mientras se está en esa parte.
#
# st.page_link no deja en el HTML ninguna marca de la página
# activa, así que cada enlace va en un contenedor con clave
# (clase st-key-...) y se pinta el activo por CSS.
# --------------------------------------------------

SECCIONES_MENU = [
    ("Analizar", ["como_nos_fue", "que_cambio", "proxima_jornada"]),
    ("Datos", ["preparar_datos"]),
]

TAREAS = ["cargar_jornada", "jornadas_guardadas", "columnas", "explorar"]

# Texto del menú sobre el bordó oscuro (utils/tema.py, MENU_FONDO).
TEXTO_MENU = "#f5dcdc"
TEXTO_ROTULO = "#e0a9a9"


def clave_actual(pagina):

    return next(
        (clave for clave, p in PAGINAS.items() if p.title == pagina.title),
        None
    )


def mostrar_menu(pagina):

    actual = clave_actual(pagina)
    en_datos = actual == "preparar_datos" or actual in TAREAS

    with st.sidebar:

        for titulo, claves in SECCIONES_MENU:

            with st.container(key=f"rotulo_{titulo.lower()}"):
                st.caption(titulo)

            for clave in claves:
                with st.container(key=f"menu_{clave}"):
                    st.page_link(PAGINAS[clave])

        if en_datos:
            for clave in TAREAS:
                with st.container(key=f"menu_tarea_{clave}"):
                    st.page_link(PAGINAS[clave])

    activo = f"menu_tarea_{actual}" if actual in TAREAS else f"menu_{actual}"

    st.markdown(
        f"""
        <style>
        [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {{
            gap: 0.15rem;
        }}
        [class*="st-key-menu_"] a {{
            border-left: 3px solid transparent;
            border-radius: 0 0.5rem 0.5rem 0;
        }}
        [class*="st-key-rotulo_"] {{
            margin-top: 0.9rem;
        }}
        [data-testid="stSidebar"] a p,
        [data-testid="stSidebar"] a span {{
            color: {TEXTO_MENU} !important;
        }}
        [data-testid="stSidebar"] a:hover {{
            background: rgba(255, 255, 255, 0.08);
        }}
        [class*="st-key-rotulo_"] p {{
            color: {TEXTO_ROTULO};
            font-size: 0.8rem;
            letter-spacing: 0.02em;
        }}
        [class*="st-key-menu_tarea_"] {{
            padding-left: 1.4rem;
        }}
        [class*="st-key-menu_tarea_"] a p {{
            white-space: normal;
            font-size: 0.9rem;
        }}
        .st-key-{activo} a {{
            background: rgba(255, 255, 255, 0.16);
            border-left-color: #ffffff;
        }}
        .st-key-{activo} a p,
        .st-key-{activo} a span {{
            color: #ffffff !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    return actual
