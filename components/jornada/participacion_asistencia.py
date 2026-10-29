import streamlit as st
import plotly.express as px

from utils.limpieza_datos import (
    detectar_columnas_asistencia,
    construir_asistencia_larga,
)


def mostrar_asistencia_participacion(df):

    columnas_asistencia = detectar_columnas_asistencia(df)

    if not columnas_asistencia:
        return

    asistencia_larga = construir_asistencia_larga(
        df,
        columnas_asistencia
    )

    asistencia_dia = (
        asistencia_larga[
            asistencia_larga["asistio"]
        ]
        .groupby("fecha")
        .size()
        .reset_index(name="asistentes")
        .sort_values("fecha")
    )

    if asistencia_dia.empty:
        return

    dia_pico = asistencia_dia.loc[
        asistencia_dia["asistentes"].idxmax()
    ]

    st.divider()

    st.markdown(
        "#### ¿Cómo evolucionó la asistencia durante la jornada?"
    )

    st.caption(
        "Se muestra la cantidad de asistentes registrados en cada día de la jornada."
    )

    fig_fecha = px.line(
        asistencia_dia,
        x="fecha",
        y="asistentes",
        markers=True
    )

    fig_fecha.add_scatter(
        x=[dia_pico["fecha"]],
        y=[dia_pico["asistentes"]],
        mode="markers",
        marker=dict(size=14),
        name="Día con mayor concurrencia"
    )

    fig_fecha.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Asistentes"
    )

    st.plotly_chart(
        fig_fecha,
        use_container_width=True,
        key="grafico_participacion_fecha"
    )

    st.info(
        f"La mayor concurrencia se registró el "
        f"**{dia_pico['fecha'].strftime('%d/%m/%Y')}**, "
        f"con **{int(dia_pico['asistentes'])} asistentes**."
    )