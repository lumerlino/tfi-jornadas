import streamlit as st

from views.como_nos_fue import mostrar_como_nos_fue
from views.que_cambio import mostrar_que_cambio
from views.analizar_jornada import mostrar_analizar_jornada
from views.historico import mostrar_historico
from views.configuracion_columnas import mostrar_configuracion_columnas
from views.gestion_cargas import mostrar_gestion_cargas
from utils.tema import mostrar_encabezado


st.set_page_config(
    page_title="Jornadas de Investigación",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# OPCIONES DE NAVEGACIÓN
# --------------------------------------------------

opciones = [
    "🏠 Cómo nos fue",
    "🔍 Qué cambió",
    "📤 Analizar jornada",
    "📊 Histórico",
    "⚙️ Configuración",
    "🗑️ Gestionar cargas"
]


# --------------------------------------------------
# ESTADO DE NAVEGACIÓN
# --------------------------------------------------

if "pagina" not in st.session_state:

    st.session_state["pagina"] = (
        "🏠 Cómo nos fue"
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

mostrar_encabezado()


if pagina == "🏠 Cómo nos fue":

    mostrar_como_nos_fue()


elif pagina == "🔍 Qué cambió":

    mostrar_que_cambio()


elif pagina == "📤 Analizar jornada":

    mostrar_analizar_jornada()


elif pagina == "📊 Histórico":

    mostrar_historico()


elif pagina == "⚙️ Configuración":

    mostrar_configuracion_columnas()


elif pagina == "🗑️ Gestionar cargas":

    mostrar_gestion_cargas()