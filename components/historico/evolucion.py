import streamlit as st
import plotly.express as px


def mostrar_evolucion_historica(df_historico):

    st.markdown(
        "### Evolución de la participación"
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
        .sort_values("anio")
    )


    # --------------------------------------------------
    # PASAMOS A FORMATO LARGO
    # --------------------------------------------------

    resumen_largo = (
        resumen_anual
        .melt(
            id_vars="anio",
            value_vars=[
                "participantes_unicos",
                "participaciones"
            ],
            var_name="indicador",
            value_name="cantidad"
        )
    )


    nombres_indicadores = {
        "participantes_unicos": "Participantes únicos",
        "participaciones": "Participaciones"
    }


    resumen_largo["indicador"] = (
        resumen_largo["indicador"]
        .map(nombres_indicadores)
    )


    # --------------------------------------------------
    # GRÁFICO
    # --------------------------------------------------

    fig_evolucion = px.line(
        resumen_largo,
        x="anio",
        y="cantidad",
        color="indicador",
        markers=True,
        text="cantidad"
    )


    fig_evolucion.update_traces(
        textposition="top center"
    )


    fig_evolucion.update_layout(
        xaxis_title="Año",
        yaxis_title="Cantidad",
        legend_title="",
        xaxis=dict(
            tickmode="linear",
            dtick=1
        )
    )


    st.plotly_chart(
        fig_evolucion,
        use_container_width=True,
        key="grafico_evolucion_historica"
    )