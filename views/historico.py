import streamlit as st

from utils.historico_datos import cargar_historico

from components.historico.indicadores import mostrar_indicadores_historicos
from components.historico.evolucion import mostrar_evolucion_historica
from components.historico.metricas import mostrar_metricas_historicas
from components.historico.composicion import mostrar_composicion_historica
from components.historico.comparacion import mostrar_comparacion_historica


def mostrar_historico():

    st.title("Histórico de Jornadas")

    df_historico = cargar_historico()

    if df_historico.empty:
        st.info("Todavía no hay jornadas guardadas en el histórico.")
        return

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📌 Resumen",
            "📈 Evolución",
            "👥 Composición",
            "🔎 Comparar jornadas"
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
                    "id_participante",
                    "size"
                ),
                participantes_unicos=(
                    "id_participante",
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

        mostrar_metricas_historicas(
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
    # COMPARACIÓN
    # --------------------------------------------------

    with tab4:

        mostrar_comparacion_historica(
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