import streamlit as st
import plotly.express as px


def mostrar_composicion_historica(df_historico):

    st.markdown(
        "### Evolución de la composición de participantes"
    )


    dimension = st.selectbox(
        "Analizar evolución por",
        [
            "Investigador Carreras",
            "Rol principal",
            "Miembro UNLa"
        ],
        key="dimension_historica"
    )


    columnas = {
        "Investigador Carreras": "Investigador Carreras",
        "Rol principal": "Rol principal",
        "Miembro UNLa": "Miembro UNLa"
    }


    columna = columnas[
        dimension
    ]


    # --------------------------------------------------
    # PARTICIPANTES ÚNICOS POR AÑO Y DIMENSIÓN
    # --------------------------------------------------

    resumen = (
        df_historico
        .dropna(
            subset=[
                "documento",
                columna
            ]
        )
        .groupby(
            [
                "anio",
                columna
            ]
        )
        .agg(
            participantes=(
                "documento",
                "nunique"
            )
        )
        .reset_index()
        .sort_values("anio")
    )


    # --------------------------------------------------
    # GRÁFICO DE EVOLUCIÓN
    # --------------------------------------------------

    fig_evolucion = px.line(
        resumen,
        x="anio",
        y="participantes",
        color=columna,
        markers=True
    )


    fig_evolucion.update_layout(
        xaxis_title="Año",
        yaxis_title="Participantes únicos",
        legend_title=dimension,
        xaxis=dict(
            tickmode="linear",
            dtick=1
        )
    )


    st.plotly_chart(
        fig_evolucion,
        use_container_width=True,
        key="grafico_composicion_historica"
    )


    # --------------------------------------------------
    # MATRIZ DE COMPARACIÓN
    # --------------------------------------------------

    st.markdown(
        "#### Comparación entre años"
    )


    matriz = (
        resumen
        .pivot(
            index=columna,
            columns="anio",
            values="participantes"
        )
        .fillna(0)
    )


    fig_matriz = px.imshow(
        matriz,
        text_auto=True,
        aspect="auto",
        labels={
            "x": "Año",
            "y": dimension,
            "color": "Participantes"
        }
    )


    st.plotly_chart(
        fig_matriz,
        use_container_width=True,
        key="grafico_matriz_composicion_historica"
    )