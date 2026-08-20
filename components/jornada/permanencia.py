import streamlit as st
import plotly.express as px

from utils.calidad_datos import obtener_mascaras_calidad


def mostrar_permanencia(df):

    mascaras = obtener_mascaras_calidad(df)

    df_permanencia = df[
        mascaras["permanencia"]
    ].copy()

    st.subheader(
        "Permanencia de los participantes"
    )

    if len(df_permanencia) == 0:
        st.warning(
            "No hay registros válidos suficientes "
            "para analizar la permanencia."
        )
        return


    # --------------------------------------------------
    # CLASIFICACIÓN DE PERMANENCIA
    # --------------------------------------------------

    def clasificar_permanencia(minutos):

        if minutos < 60:
            return "Menos de 1 hora"

        elif minutos < 120:
            return "1 a 2 horas"

        elif minutos < 180:
            return "2 a 3 horas"

        else:
            return "Más de 3 horas"


    df_permanencia["rango_permanencia"] = (
        df_permanencia["permanencia_minutos"]
        .apply(clasificar_permanencia)
    )


    orden = [
        "Menos de 1 hora",
        "1 a 2 horas",
        "2 a 3 horas",
        "Más de 3 horas"
    ]


    distribucion = (
        df_permanencia["rango_permanencia"]
        .value_counts()
        .reindex(
            orden,
            fill_value=0
        )
        .reset_index()
    )

    distribucion.columns = [
        "rango",
        "cantidad"
    ]


    # --------------------------------------------------
    # PERMANENCIA PROMEDIO POR ACTIVIDAD
    # --------------------------------------------------

    permanencia_actividad = (
        df_permanencia
        .groupby("actividad")["permanencia_minutos"]
        .mean()
        .reset_index()
        .sort_values(
            "permanencia_minutos",
            ascending=True
        )
    )


    # --------------------------------------------------
    # DOS GRÁFICOS PRINCIPALES
    # --------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        st.markdown(
            "#### Distribución de permanencia"
        )

        fig_distribucion = px.bar(
            distribucion,
            x="rango",
            y="cantidad",
            text="cantidad"
        )

        fig_distribucion.update_layout(
            xaxis_title="",
            yaxis_title="Participaciones"
        )

        st.plotly_chart(
            fig_distribucion,
            use_container_width=True,
            key="grafico_distribucion_permanencia"
        )


    with col2:

        st.markdown(
            "#### Permanencia promedio por actividad"
        )

        fig_perm_actividad = px.bar(
            permanencia_actividad,
            x="permanencia_minutos",
            y="actividad",
            orientation="h",
            text_auto=".0f"
        )

        fig_perm_actividad.update_layout(
            xaxis_title="Minutos promedio",
            yaxis_title=""
        )

        st.plotly_chart(
            fig_perm_actividad,
            use_container_width=True,
            key="grafico_permanencia_actividad"
        )


    # --------------------------------------------------
    # RETIRO ANTICIPADO
    # --------------------------------------------------

    st.markdown(
        "#### Retiro antes del final de la actividad"
    )

    df_permanencia["retiro_anticipado"] = (
        df_permanencia["hora_egreso"]
        <
        df_permanencia["hora_fin_actividad"]
    )


    retiro_actividad = (
        df_permanencia
        .groupby("actividad")
        .agg(
            participantes=("id_participante", "count"),
            retiros_anticipados=(
                "retiro_anticipado",
                "sum"
            )
        )
        .reset_index()
    )


    retiro_actividad["porcentaje_retiro"] = (
        retiro_actividad["retiros_anticipados"]
        / retiro_actividad["participantes"]
    ) * 100


    retiro_actividad = (
        retiro_actividad
        .sort_values(
            "porcentaje_retiro",
            ascending=True
        )
    )


    fig_retiro = px.bar(
        retiro_actividad,
        x="porcentaje_retiro",
        y="actividad",
        orientation="h",
        text_auto=".1f",
        hover_data={
            "participantes": True,
            "retiros_anticipados": True,
            "porcentaje_retiro": ":.1f"
        }
    )

    fig_retiro.update_layout(
        xaxis_title="Participantes que se retiraron antes (%)",
        yaxis_title=""
    )

    st.plotly_chart(
        fig_retiro,
        use_container_width=True,
        key="grafico_retiro_anticipado"
    )


    # --------------------------------------------------
    # COMPARACIÓN DINÁMICA
    # --------------------------------------------------

    st.markdown(
        "#### Comparar permanencia por"
    )

    dimension_perm = st.selectbox(
        "Seleccioná una dimensión",
        [
            "Carrera",
            "Tipo de participante",
            "Institución"
        ],
        key="dimension_permanencia"
    )


    columnas_perm = {
        "Carrera": "carrera",
        "Tipo de participante": "tipo_participante",
        "Institución": "institucion"
    }


    columna_perm = columnas_perm[
        dimension_perm
    ]


    permanencia_dimension = (
        df_permanencia
        .groupby(
            columna_perm
        )["permanencia_minutos"]
        .mean()
        .reset_index()
        .sort_values(
            "permanencia_minutos",
            ascending=False
        )
    )


    fig_perm_dimension = px.bar(
        permanencia_dimension,
        x=columna_perm,
        y="permanencia_minutos",
        text_auto=".0f"
    )

    fig_perm_dimension.update_layout(
        xaxis_title="",
        yaxis_title="Minutos promedio"
    )

    st.plotly_chart(
        fig_perm_dimension,
        use_container_width=True,
        key="grafico_permanencia_dimension"
    )