import streamlit as st
import plotly.express as px


def mostrar_participacion(df):

    st.subheader("Participación en la jornada")


    # --------------------------------------------------
    # PARTICIPACIÓN POR ACTIVIDAD
    # --------------------------------------------------

    participacion_actividad = (
        df
        .groupby("actividad")
        .size()
        .reset_index(name="participaciones")
        .sort_values(
            "participaciones",
            ascending=True
        )
    )


    # --------------------------------------------------
    # PERFIL DE PARTICIPANTES
    # --------------------------------------------------

    participacion_tipo = (
        df
        .groupby("tipo_participante")
        .size()
        .reset_index(name="participaciones")
    )


    col1, col2 = st.columns([2, 1])


    with col1:

        st.markdown(
            "#### Actividades con mayor participación"
        )

        fig_actividad = px.bar(
            participacion_actividad,
            x="participaciones",
            y="actividad",
            orientation="h",
            text="participaciones"
        )

        fig_actividad.update_layout(
            xaxis_title="Participaciones",
            yaxis_title="",
            showlegend=False
        )

        st.plotly_chart(
            fig_actividad,
            use_container_width=True,
            key="grafico_participacion_actividad"
        )


    with col2:

        st.markdown(
            "#### Perfil de participantes"
        )

        fig_tipo = px.pie(
            participacion_tipo,
            names="tipo_participante",
            values="participaciones",
            hole=0.45
        )

        st.plotly_chart(
            fig_tipo,
            use_container_width=True,
            key="grafico_perfil_participantes"
        )


    # --------------------------------------------------
    # PARTICIPACIÓN POR FECHA
    # --------------------------------------------------

    participacion_fecha = (
        df
        .groupby(
            [
                "fecha",
                "fecha_texto"
            ]
        )
        .size()
        .reset_index(
            name="participaciones"
        )
        .sort_values("fecha")
    )

    st.markdown(
        "#### Participación durante la jornada"
    )

    fig_fecha = px.line(
        participacion_fecha,
        x="fecha_texto",
        y="participaciones",
        markers=True
    )

    fig_fecha.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Participaciones"
    )

    st.plotly_chart(
        fig_fecha,
        use_container_width=True,
        key="grafico_participacion_fecha"
    )


    # --------------------------------------------------
    # ANÁLISIS DINÁMICO
    # --------------------------------------------------

    st.markdown(
        "#### Analizar participación por"
    )

    dimension = st.selectbox(
        "Seleccioná una dimensión",
        [
            "Carrera",
            "Institución",
            "Tipo de participante"
        ],
        key="dimension_participacion"
    )


    columnas = {
        "Carrera": "carrera",
        "Institución": "institucion",
        "Tipo de participante": "tipo_participante"
    }


    columna_elegida = columnas[
        dimension
    ]


    participacion_dimension = (
        df
        .groupby(columna_elegida)
        .size()
        .reset_index(
            name="participaciones"
        )
        .sort_values(
            "participaciones",
            ascending=False
        )
    )


    fig_dimension = px.bar(
        participacion_dimension,
        x=columna_elegida,
        y="participaciones",
        text="participaciones"
    )

    fig_dimension.update_layout(
        xaxis_title="",
        yaxis_title="Participaciones"
    )

    st.plotly_chart(
        fig_dimension,
        use_container_width=True,
        key="grafico_dimension_participacion"
    )


    # --------------------------------------------------
    # RELACIÓN ENTRE VARIABLES
    # --------------------------------------------------

    st.markdown(
        "#### Relación entre variables"
    )

    relacion = st.selectbox(
        "Seleccioná una relación",
        [
            "Actividad × Carrera",
            "Actividad × Tipo de participante"
        ],
        key="relacion_participacion"
    )


    if relacion == "Actividad × Carrera":

        matriz = (
            df
            .groupby(
                [
                    "actividad",
                    "carrera"
                ]
            )
            .size()
            .reset_index(
                name="participaciones"
            )
            .pivot(
                index="actividad",
                columns="carrera",
                values="participaciones"
            )
            .fillna(0)
        )

        titulo_x = "Carrera"


    elif relacion == "Actividad × Tipo de participante":

        matriz = (
            df
            .groupby(
                [
                    "actividad",
                    "tipo_participante"
                ]
            )
            .size()
            .reset_index(
                name="participaciones"
            )
            .pivot(
                index="actividad",
                columns="tipo_participante",
                values="participaciones"
            )
            .fillna(0)
        )

        titulo_x = "Tipo de participante"


    fig_matriz = px.imshow(
        matriz,
        text_auto=True,
        aspect="auto",
        labels={
            "x": titulo_x,
            "y": "Actividad",
            "color": "Participaciones"
        }
    )

    st.plotly_chart(
        fig_matriz,
        use_container_width=True,
        key="grafico_relacion_participacion"
    )