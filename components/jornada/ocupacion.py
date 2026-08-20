import streamlit as st
import plotly.express as px

from utils.calidad_datos import obtener_mascaras_calidad


def mostrar_ocupacion(df):

    st.subheader("Ocupación de aulas y actividades")

    mascaras = obtener_mascaras_calidad(df)

    df_ocupacion = df[
        mascaras["ocupacion"]
    ].copy()


    if len(df_ocupacion) == 0:

        st.warning(
            "No hay registros válidos suficientes "
            "para analizar la ocupación."
        )

        return


    # --------------------------------------------------
    # RESUMEN POR ACTIVIDAD
    # --------------------------------------------------

    ocupacion_actividad = (
        df_ocupacion
        .groupby(
            [
                "actividad",
                "aula",
                "capacidad_aula"
            ]
        )
        .agg(
            participantes=(
                "id_participante",
                "nunique"
            )
        )
        .reset_index()
    )


    ocupacion_actividad["ocupacion_porcentaje"] = (
        ocupacion_actividad["participantes"]
        / ocupacion_actividad["capacidad_aula"]
    ) * 100


    ocupacion_actividad["lugares_disponibles"] = (
        ocupacion_actividad["capacidad_aula"]
        - ocupacion_actividad["participantes"]
    )


    # --------------------------------------------------
    # CLASIFICACIÓN
    # --------------------------------------------------

    def clasificar_ocupacion(porcentaje):

        if porcentaje >= 100:
            return "Capacidad alcanzada"

        elif porcentaje >= 80:
            return "Alta ocupación"

        elif porcentaje >= 50:
            return "Ocupación media"

        else:
            return "Baja ocupación"


    ocupacion_actividad["nivel_ocupacion"] = (
        ocupacion_actividad["ocupacion_porcentaje"]
        .apply(clasificar_ocupacion)
    )


    # --------------------------------------------------
    # INDICADORES
    # --------------------------------------------------

    ocupacion_promedio = (
        ocupacion_actividad["ocupacion_porcentaje"]
        .mean()
    )

    actividad_mas_ocupada = (
        ocupacion_actividad
        .sort_values(
            "ocupacion_porcentaje",
            ascending=False
        )
        .iloc[0]
    )

    actividad_menos_ocupada = (
        ocupacion_actividad
        .sort_values(
            "ocupacion_porcentaje"
        )
        .iloc[0]
    )

    actividades_riesgo = (
        ocupacion_actividad[
            ocupacion_actividad["ocupacion_porcentaje"] >= 80
        ]
        .shape[0]
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Ocupación promedio",
            f"{ocupacion_promedio:.1f}%"
        )


    with col2:

        st.metric(
            "Mayor ocupación",
            f"{actividad_mas_ocupada['ocupacion_porcentaje']:.1f}%"
        )

        st.caption(
            actividad_mas_ocupada["actividad"]
        )


    with col3:

        st.metric(
            "Menor ocupación",
            f"{actividad_menos_ocupada['ocupacion_porcentaje']:.1f}%"
        )

        st.caption(
            actividad_menos_ocupada["actividad"]
        )


    with col4:

        st.metric(
            "Actividades con alta ocupación",
            actividades_riesgo
        )


    st.divider()


    # --------------------------------------------------
    # OCUPACIÓN POR ACTIVIDAD
    # --------------------------------------------------

    col1, col2 = st.columns([2, 1])


    with col1:

        st.markdown(
            "#### Ocupación por actividad"
        )

        ocupacion_ordenada = (
            ocupacion_actividad
            .sort_values(
                "ocupacion_porcentaje",
                ascending=True
            )
        )


        fig_ocupacion = px.bar(
            ocupacion_ordenada,
            x="ocupacion_porcentaje",
            y="actividad",
            orientation="h",
            text_auto=".1f",
            hover_data={
                "aula": True,
                "participantes": True,
                "capacidad_aula": True,
                "lugares_disponibles": True,
                "ocupacion_porcentaje": ":.1f"
            }
        )

        fig_ocupacion.update_layout(
            xaxis_title="Ocupación (%)",
            yaxis_title=""
        )

        st.plotly_chart(
            fig_ocupacion,
            use_container_width=True,
            key="grafico_ocupacion_actividad"
        )


    # --------------------------------------------------
    # DISTRIBUCIÓN SEGÚN NIVEL
    # --------------------------------------------------

    with col2:

        st.markdown(
            "#### Estado de ocupación"
        )

        resumen_nivel = (
            ocupacion_actividad[
                "nivel_ocupacion"
            ]
            .value_counts()
            .reset_index()
        )

        resumen_nivel.columns = [
            "nivel",
            "cantidad"
        ]


        fig_nivel = px.pie(
            resumen_nivel,
            names="nivel",
            values="cantidad",
            hole=0.45
        )

        st.plotly_chart(
            fig_nivel,
            use_container_width=True,
            key="grafico_nivel_ocupacion"
        )


    # --------------------------------------------------
    # CAPACIDAD VS PARTICIPANTES
    # --------------------------------------------------

    st.markdown(
        "#### Capacidad disponible vs participantes"
    )


    capacidad_comparacion = (
        ocupacion_actividad[
            [
                "actividad",
                "participantes",
                "capacidad_aula"
            ]
        ]
        .rename(
            columns={
                "capacidad_aula": "capacidad"
            }
        )
    )


    capacidad_larga = (
        capacidad_comparacion
        .melt(
            id_vars="actividad",
            value_vars=[
                "participantes",
                "capacidad"
            ],
            var_name="tipo",
            value_name="cantidad"
        )
    )


    fig_capacidad = px.bar(
        capacidad_larga,
        x="actividad",
        y="cantidad",
        color="tipo",
        barmode="group",
        text="cantidad"
    )

    fig_capacidad.update_layout(
        xaxis_title="",
        yaxis_title="Personas",
        legend_title=""
    )

    st.plotly_chart(
        fig_capacidad,
        use_container_width=True,
        key="grafico_capacidad_participantes"
    )


    # --------------------------------------------------
    # INTERPRETACIÓN
    # --------------------------------------------------

    st.markdown(
        "#### Actividades a revisar"
    )


    actividades_alta_ocupacion = (
        ocupacion_actividad[
            ocupacion_actividad["ocupacion_porcentaje"] >= 80
        ]
        .sort_values(
            "ocupacion_porcentaje",
            ascending=False
        )
    )


    actividades_baja_ocupacion = (
        ocupacion_actividad[
            ocupacion_actividad["ocupacion_porcentaje"] < 50
        ]
        .sort_values(
            "ocupacion_porcentaje"
        )
    )


    col1, col2 = st.columns(2)


    with col1:

        st.write(
            "**Alta ocupación**"
        )

        if len(actividades_alta_ocupacion) == 0:

            st.success(
                "No se detectaron actividades con ocupación superior al 80%."
            )

        else:

            for _, fila in actividades_alta_ocupacion.iterrows():

                st.warning(
                    f"{fila['actividad']}: "
                    f"{fila['ocupacion_porcentaje']:.1f}% "
                    f"({fila['participantes']} de "
                    f"{fila['capacidad_aula']} lugares)"
                )


    with col2:

        st.write(
            "**Baja ocupación**"
        )

        if len(actividades_baja_ocupacion) == 0:

            st.success(
                "No se detectaron actividades con ocupación inferior al 50%."
            )

        else:

            for _, fila in actividades_baja_ocupacion.iterrows():

                st.info(
                    f"{fila['actividad']}: "
                    f"{fila['ocupacion_porcentaje']:.1f}% "
                    f"({fila['participantes']} de "
                    f"{fila['capacidad_aula']} lugares)"
                )


    # --------------------------------------------------
    # DETALLE
    # --------------------------------------------------

    with st.expander(
        "Ver detalle de ocupación"
    ):

        tabla_ocupacion = (
            ocupacion_actividad
            .copy()
            .sort_values(
                "ocupacion_porcentaje",
                ascending=False
            )
        )

        tabla_ocupacion[
            "ocupacion_porcentaje"
        ] = (
            tabla_ocupacion[
                "ocupacion_porcentaje"
            ]
            .round(1)
        )

        tabla_ocupacion = (
            tabla_ocupacion
            .rename(
                columns={
                    "actividad": "Actividad",
                    "aula": "Aula",
                    "capacidad_aula": "Capacidad",
                    "participantes": "Participantes",
                    "lugares_disponibles": "Lugares disponibles",
                    "ocupacion_porcentaje": "Ocupación (%)",
                    "nivel_ocupacion": "Estado"
                }
            )
        )

        st.dataframe(
            tabla_ocupacion,
            use_container_width=True,
            hide_index=True
        )