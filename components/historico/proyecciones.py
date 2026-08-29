import streamlit as st
import plotly.graph_objects as go

from utils.proyecciones import calcular_tendencia


def mostrar_proyecciones(df_historico):

    st.markdown("### Proyección de asistencia")

    tendencia = calcular_tendencia(df_historico)

    if not tendencia["suficiente"]:

        faltan = (
            tendencia["anios_necesarios"]
            - tendencia["anios_disponibles"]
        )

        st.info(
            f"Faltan {faltan} edición/ediciones más para poder calcular "
            f"una proyección (hay {tendencia['anios_disponibles']} de "
            f"{tendencia['anios_necesarios']} necesarias)."
        )

        return

    serie = tendencia["serie"]

    anios_extendidos = (
        serie["anio"].tolist()
        + [tendencia["proximo_anio"]]
    )

    valores_tendencia = [
        tendencia["pendiente"] * anio + tendencia["ordenada"]
        for anio in anios_extendidos
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=serie["anio"],
            y=serie["asistentes"],
            mode="markers+lines",
            name="Asistentes reales"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=anios_extendidos,
            y=valores_tendencia,
            mode="lines",
            name="Tendencia (regresión lineal)",
            line=dict(dash="dash")
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[tendencia["proximo_anio"]],
            y=[tendencia["proyeccion"]],
            mode="markers",
            name="Proyección",
            marker=dict(size=14, color="red")
        )
    )

    fig.update_layout(
        xaxis_title="Año",
        yaxis_title="Asistentes",
        xaxis=dict(tickmode="linear", dtick=1)
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="grafico_proyeccion"
    )

    st.metric(
        f"Proyección {tendencia['proximo_anio']}",
        f"{tendencia['proyeccion']:.0f} asistentes"
    )

    st.caption(
        f"Ajuste de regresión lineal sobre {tendencia['anios_disponibles']} "
        f"ediciones. R² = {tendencia['r2']:.2f}. Con pocas ediciones el "
        f"ajuste tiene muy baja confianza estadística — interpretar como "
        f"orientativo, no como una predicción certera."
    )
