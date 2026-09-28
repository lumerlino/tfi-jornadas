import streamlit as st

from components.navegacion import PAGINAS
from views.como_nos_fue import mostrar_como_nos_fue
from views.que_cambio import mostrar_que_cambio
from views.proxima_jornada import mostrar_proxima_jornada
from views.analizar_jornada import mostrar_analizar_jornada
from views.historico import mostrar_historico
from views.configuracion_columnas import mostrar_configuracion_columnas
from views.gestion_cargas import mostrar_gestion_cargas
from views.preparar_datos import mostrar_preparar_datos
from utils.tema import mostrar_marco


st.set_page_config(
    page_title="Jornadas de Investigación",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# NAVEGACIÓN
#
# En el menú: las tres preguntas que se hace quien organiza la
# jornada y una sola entrada "Preparar datos" (la trastienda), que
# abre una pantalla con las tareas. Las tareas no van en el menú,
# pero siguen siendo páginas con URL propia. El análisis completo
# anterior (las pestañas del histórico) queda en "Explorar en
# detalle".
# --------------------------------------------------

PAGINAS.update({
    "como_nos_fue": st.Page(
        mostrar_como_nos_fue,
        title="Cómo nos fue",
        icon=":material/home:",
        url_path="como-nos-fue",
        default=True
    ),
    "que_cambio": st.Page(
        mostrar_que_cambio,
        title="Qué cambió",
        icon=":material/compare_arrows:",
        url_path="que-cambio"
    ),
    "proxima_jornada": st.Page(
        mostrar_proxima_jornada,
        title="Nuestra próxima jornada",
        icon=":material/flag:",
        url_path="proxima-jornada"
    ),
    "preparar_datos": st.Page(
        mostrar_preparar_datos,
        title="Preparar datos",
        icon=":material/settings:",
        url_path="preparar-datos"
    ),
    "cargar_jornada": st.Page(
        mostrar_analizar_jornada,
        title="Nueva jornada",
        icon=":material/upload_file:",
        url_path="nueva-jornada"
    ),
    "jornadas_guardadas": st.Page(
        mostrar_gestion_cargas,
        title="Jornadas guardadas",
        icon=":material/folder_open:",
        url_path="jornadas-guardadas"
    ),
    "columnas": st.Page(
        mostrar_configuracion_columnas,
        title="Columnas del formulario",
        icon=":material/view_column:",
        url_path="columnas"
    ),
    "explorar": st.Page(
        mostrar_historico,
        title="Explorar en detalle",
        icon=":material/query_stats:",
        url_path="explorar"
    ),
})

TAREAS = ["cargar_jornada", "jornadas_guardadas", "columnas", "explorar"]

# El menú lo dibujamos nosotros (position="hidden"): st.navigation
# mostraría todas las páginas, incluidas las tareas.
pagina = st.navigation(list(PAGINAS.values()), position="hidden")

with st.sidebar:

    st.page_link(PAGINAS["como_nos_fue"])
    st.page_link(PAGINAS["que_cambio"])
    st.page_link(PAGINAS["proxima_jornada"])

    st.divider()

    st.page_link(PAGINAS["preparar_datos"])

    tarea_actual = next(
        (clave for clave in TAREAS if PAGINAS[clave].url_path == pagina.url_path),
        None
    )

    if tarea_actual:
        st.caption(f"↳ {pagina.title}")


# --------------------------------------------------
# CONTENIDO
# --------------------------------------------------

mostrar_marco()

if tarea_actual:
    st.page_link(PAGINAS["preparar_datos"], label="Volver a Preparar datos", icon=":material/arrow_back:")

pagina.run()
