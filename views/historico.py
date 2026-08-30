import streamlit as st

from utils.historico_datos import cargar_historico

from components.historico.indicadores import mostrar_indicadores_historicos
from components.historico.evolucion import mostrar_evolucion_historica
from components.historico.composicion import mostrar_composicion_historica
from components.historico.proyecciones import mostrar_proyecciones
from components.historico.escenarios import mostrar_escenarios
from components.historico.kpis_cruzados import mostrar_kpis_cruzados
from components.historico.objetivos import mostrar_objetivos


def mostrar_historico():

    st.title("Histórico de Jornadas")

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

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
        [
            "📌 Resumen",
            "📈 Evolución",
            "👥 Composición",
            "🔮 Proyecciones",
            "🎛️ What-if",
            "🔗 KPIs cruzados",
            "🎯 Objetivos"
        ]
    )


    # --------------------------------------------------
    # RESUMEN
    # --------------------------------------------------

    with tab1:

        mostrar_indicadores_historicos(
            df_historico
        )

        st.markdown(
            "### Resumen por año"
        )

        resumen_anual = (
            df_historico
            .groupby("anio")
            .agg(
                participaciones=(
                    "documento",
                    "size"
                ),
                participantes_unicos=(
                    "documento",
                    "nunique"
                )
            )
            .reset_index()
            .sort_values(
                "anio",
                ascending=False
            )
        )

        resumen_anual = resumen_anual.rename(
            columns={
                "anio": "Año",
                "participaciones": "Participaciones",
                "participantes_unicos": "Participantes únicos"
            }
        )

        st.dataframe(
            resumen_anual,
            use_container_width=True,
            hide_index=True
        )


    # --------------------------------------------------
    # EVOLUCIÓN
    # --------------------------------------------------

    with tab2:

        mostrar_evolucion_historica(
            df_historico
        )


    # --------------------------------------------------
    # COMPOSICIÓN
    # --------------------------------------------------

    with tab3:

        mostrar_composicion_historica(
            df_historico
        )


    # --------------------------------------------------
    # PROYECCIONES
    # --------------------------------------------------

    with tab4:

        mostrar_proyecciones(
            df_historico
        )


    # --------------------------------------------------
    # WHAT-IF
    # --------------------------------------------------

    with tab5:

        mostrar_escenarios(
            df_historico
        )


    # --------------------------------------------------
    # KPIS CRUZADOS
    # --------------------------------------------------

    with tab6:

        mostrar_kpis_cruzados(
            df_historico
        )


    # --------------------------------------------------
    # OBJETIVOS
    # --------------------------------------------------

    with tab7:

        mostrar_objetivos(
            df_historico
        )


    # --------------------------------------------------
    # DATOS COMPLETOS
    # --------------------------------------------------

    with st.expander(
        "Ver datos históricos completos"
    ):

        st.dataframe(
            df_historico,
            use_container_width=True,
            hide_index=True
        )
