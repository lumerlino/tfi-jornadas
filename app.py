import streamlit as st

from components.navegacion import PAGINAS
from views.como_nos_fue import mostrar_como_nos_fue
from views.que_cambio import mostrar_que_cambio
from views.proxima_jornada import mostrar_proxima_jornada
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
# NAVEGACIÓN
#
# Arriba, las tres preguntas que se hace quien organiza la jornada.
# Abajo, "Preparar datos": la carga y administración de los datos,
# separada del recorrido principal. El análisis completo anterior
# (todas las pestañas del histórico) queda en "Explorar en detalle".
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
    "cargar_jornada": st.Page(
        mostrar_analizar_jornada,
        title="Cargar jornada nueva",
        icon=":material/upload_file:",
        url_path="cargar-jornada"
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

pagina = st.navigation({
    "": [
        PAGINAS["como_nos_fue"],
        PAGINAS["que_cambio"],
        PAGINAS["proxima_jornada"],
    ],
    "Preparar datos": [
        PAGINAS["cargar_jornada"],
        PAGINAS["jornadas_guardadas"],
        PAGINAS["columnas"],
        PAGINAS["explorar"],
    ],
})


# --------------------------------------------------
# CONTENIDO
# --------------------------------------------------

mostrar_encabezado()

pagina.run()
