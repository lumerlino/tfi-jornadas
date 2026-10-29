import streamlit as st

from components.ui import mostrar_error

from utils.historico_datos import cargar_historico
from utils.gestion_cargas import listar_cargas
from utils.jornada_guardada import reconstruir_jornada
from utils.configuracion_columnas import (
    obtener_configuraciones,
    CONFIGURACION_POR_DEFECTO
)
from utils.ui_tabs import mostrar_tabs

from components.historico.indicadores import mostrar_indicadores_historicos
from components.historico.evolucion import mostrar_evolucion_historica
from components.historico.composicion import mostrar_composicion_historica
from components.historico.proyecciones import mostrar_proyecciones
from components.historico.escenarios import mostrar_escenarios
from components.historico.kpis_cruzados import mostrar_kpis_cruzados
from components.historico.objetivos import mostrar_objetivos
from views.dashboard_jornada import mostrar_dashboard_jornada


def mostrar_historico():

    st.title("Detalle de una jornada")

    try:

        df_historico = cargar_historico()

    except Exception as error:

        st.error(
            "No se pudo conectar con la base de datos del histórico. "
            "Probá de nuevo en unos minutos; si el problema persiste, "
            "puede ser un tema de configuración o de conexión."
        )

        with st.expander("Detalle técnico"):
            st.write(f"{type(error).__name__}: {error}")

        return

    if df_historico.empty:
        st.info("Todavía no hay jornadas guardadas en el histórico.")
        return

    pestania = "🔍 Ver jornada"


    # --------------------------------------------------
    # VER JORNADA: el mismo dashboard de "Analizar jornada",
    # reconstruido a partir de una carga ya guardada (sin
    # necesidad de volver a subir el Excel).
    # --------------------------------------------------

    if pestania == "🔍 Ver jornada":

        try:

            cargas = listar_cargas()

        except Exception as error:

            st.error(
                "No se pudo conectar con la base de datos para "
                "listar las cargas guardadas."
            )

            with st.expander("Detalle técnico"):
                st.write(f"{type(error).__name__}: {error}")

            cargas = []

        if not cargas:

            st.info(
                "Todavía no hay ninguna carga guardada."
            )

        else:

            opciones_carga = {
                f"Jornada {carga['anio']} — carga N.º "
                f"{carga['numero_carga']} "
                f"({carga['cantidad_participaciones']} personas)": (
                    carga["carga_id"]
                )
                for carga in cargas
            }

            seleccion = st.selectbox(
                "Elegí una jornada guardada",
                list(opciones_carga.keys()),
                key="selector_ver_jornada"
            )

            carga_id_elegida = opciones_carga[seleccion]

            try:

                df_jornada = reconstruir_jornada(carga_id_elegida)

            except Exception as error:

                mostrar_error(error, "No se pudo abrir la jornada guardada")
                df_jornada = None

            if df_jornada is None:

                pass

            elif df_jornada.empty:

                st.warning(
                    "Esta carga no tiene participaciones guardadas."
                )

            else:

                try:

                    configuraciones_jornada = obtener_configuraciones()

                except Exception:

                    configuraciones_jornada = CONFIGURACION_POR_DEFECTO

                    st.warning(
                        "No se pudo cargar la configuración de "
                        "columnas — se están usando los filtros "
                        "por default."
                    )

                mostrar_dashboard_jornada(
                    df_jornada,
                    configuraciones_jornada
                )

