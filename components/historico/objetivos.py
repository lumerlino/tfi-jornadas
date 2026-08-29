import streamlit as st

from utils.proyecciones import calcular_tendencia
from utils.objetivos import calcular_objetivo


def mostrar_objetivos(df_historico):

    st.markdown("### Objetivos de mejora")

    tendencia = calcular_tendencia(df_historico)

    ultimo_anio = int(df_historico["anio"].max())

    col1, col2 = st.columns(2)

    with col1:

        anio_objetivo = st.number_input(
            "Año objetivo",
            min_value=ultimo_anio + 1,
            value=ultimo_anio + 1,
            step=1,
            key="anio_objetivo"
        )

    with col2:

        asistentes_objetivo = st.number_input(
            "Asistentes objetivo",
            min_value=1,
            value=1000,
            step=50,
            key="asistentes_objetivo"
        )

    resultado = calcular_objetivo(
        df_historico,
        int(anio_objetivo),
        int(asistentes_objetivo),
        tendencia
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            f"Asistentes en {resultado['anio_actual']} (última edición)",
            resultado["asistentes_actuales"]
        )

    with col2:

        st.metric(
            f"Brecha hacia el objetivo {int(anio_objetivo)}",
            resultado["brecha"],
            help="Objetivo menos asistentes de la última edición cargada."
        )

    if not resultado["tiene_tendencia"]:

        st.info(
            "Con menos de 3 ediciones no se puede comparar la brecha "
            "contra una tasa de crecimiento histórica — solo se muestra "
            "la diferencia simple entre el objetivo y el último dato real."
        )

        return

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Crecimiento anual necesario",
            f"{resultado['tasa_necesaria'] * 100:+.1f}%"
        )

    with col2:

        if resultado["tasa_historica"] is not None:

            st.metric(
                "Crecimiento anual histórico observado",
                f"{resultado['tasa_historica'] * 100:+.1f}%"
            )

    st.caption(
        "El crecimiento histórico se calcula entre la primera y la "
        "última edición cargada; incluye ediciones de demostración si "
        "las hay, así que debe leerse con la misma cautela que la "
        "proyección."
    )
