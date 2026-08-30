import streamlit as st

from views.inicio import mostrar_inicio
from views.analizar_jornada import mostrar_analizar_jornada
from views.historico import mostrar_historico
from views.configuracion_columnas import mostrar_configuracion_columnas


st.set_page_config(
    page_title="Jornadas de Investigación",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# OPCIONES DE NAVEGACIÓN
# --------------------------------------------------

opciones = [
    "🏠 Inicio",
    "📤 Analizar jornada",
    "📊 Histórico",
    "⚙️ Configuración"
]


# --------------------------------------------------
# ESTADO DE NAVEGACIÓN
# --------------------------------------------------

if "pagina" not in st.session_state:

    st.session_state["pagina"] = (
        "🏠 Inicio"
    )


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title(
    "Jornadas UNLa"
)

pagina_seleccionada = st.sidebar.radio(
    "Navegación",
    opciones,
    index=opciones.index(
        st.session_state["pagina"]
    )
)


# --------------------------------------------------
# CAMBIO DESDE EL MENÚ
# --------------------------------------------------

if (
    pagina_seleccionada
    != st.session_state["pagina"]
):

    st.session_state["pagina"] = (
        pagina_seleccionada
    )

    st.rerun()


# --------------------------------------------------
# CONTENIDO
# --------------------------------------------------

pagina = st.session_state["pagina"]


if pagina == "🏠 Inicio":

    mostrar_inicio()


elif pagina == "📤 Analizar jornada":

    mostrar_analizar_jornada()


elif pagina == "📊 Histórico":

    mostrar_historico()


elif pagina == "⚙️ Configuración":

    mostrar_configuracion_columnas()