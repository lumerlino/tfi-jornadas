import streamlit as st
import plotly.express as px

from utils.limpieza_datos import (
    detectar_columnas_asistencia,
    construir_asistencia_larga
)


def mostrar_participacion(df):

    st.subheader("Participación en la jornada")


    # --------------------------------------------------
    # PERFIL DE PARTICIPANTES
    # --------------------------------------------------

    participacion_rol = (
        df
        .groupby("Rol principal")
        .size()
        .reset_index(name="participantes")
        .sort_values(
            "participantes",
            ascending=True
        )
    )


    col1, col2 = st.columns([2, 1])


    with col1:

        st.markdown(
            "#### Participantes por rol"
        )

        fig_rol = px.bar(
            participacion_rol,
            x="participantes",
            y="Rol principal",
            orientation="h",
            text="participantes"
        )

        fig_rol.update_layout(
            xaxis_title="Participantes",
            yaxis_title="",
            showlegend=False
        )

        st.plotly_chart(
            fig_rol,
            use_container_width=True,
            key="grafico_participacion_rol"
        )


    with col2:

        st.markdown(
            "#### Miembros UNLa"
        )

        participacion_unla = (
            df
            .groupby("Miembro UNLa")
            .size()
            .reset_index(name="participantes")
        )

        fig_unla = px.pie(
            participacion_unla,
            names="Miembro UNLa",
            values="participantes",
            hole=0.45
        )

        st.plotly_chart(
            fig_unla,
            use_container_width=True,
            key="grafico_perfil_participantes"
        )


    # --------------------------------------------------
    # ASISTENCIA POR DÍA
    # --------------------------------------------------

    columnas_asistencia = detectar_columnas_asistencia(df)

    if columnas_asistencia:

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

        dia_pico = asistencia_dia.loc[
            asistencia_dia["asistentes"].idxmax()
        ]

        st.markdown(
            "#### Asistencia durante la jornada"
        )

        st.metric(
            "Día con mayor concurrencia",
            dia_pico["fecha"].strftime("%d/%m/%Y"),
            f"{int(dia_pico['asistentes'])} asistentes"
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
            marker=dict(size=14, color="red"),
            name="Día pico"
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


    # --------------------------------------------------
    # ANÁLISIS DINÁMICO
    # --------------------------------------------------

    st.markdown(
        "#### Analizar participación por"
    )

    dimension = st.selectbox(
        "Seleccioná una dimensión",
        [
            "Rol principal",
            "Investigador Carreras",
            "Tipo inscripción",
            "Source"
        ],
        key="dimension_participacion"
    )


    participacion_dimension = (
        df
        .groupby(dimension)
        .size()
        .reset_index(
            name="participantes"
        )
        .sort_values(
            "participantes",
            ascending=False
        )
        .head(15)
    )


    fig_dimension = px.bar(
        participacion_dimension,
        x=dimension,
        y="participantes",
        text="participantes"
    )

    fig_dimension.update_layout(
        xaxis_title="",
        yaxis_title="Participantes"
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
            "Rol principal × Miembro UNLa",
            "Rol principal × Tipo inscripción"
        ],
        key="relacion_participacion"
    )


    if relacion == "Rol principal × Miembro UNLa":

        columna_cruce = "Miembro UNLa"

    else:

        columna_cruce = "Tipo inscripción"


    matriz = (
        df
        .groupby(
            [
                "Rol principal",
                columna_cruce
            ]
        )
        .size()
        .reset_index(
            name="participantes"
        )
        .pivot(
            index="Rol principal",
            columns=columna_cruce,
            values="participantes"
        )
        .fillna(0)
    )


    fig_matriz = px.imshow(
        matriz,
        text_auto=True,
        aspect="auto",
        labels={
            "x": columna_cruce,
            "y": "Rol principal",
            "color": "Participantes"
        }
    )

    st.plotly_chart(
        fig_matriz,
        use_container_width=True,
        key="grafico_relacion_participacion"
    )
