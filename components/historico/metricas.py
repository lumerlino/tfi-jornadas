import streamlit as st
import plotly.express as px
import pandas as pd


def mostrar_metricas_historicas(df_historico):

    st.markdown(
        "### Evolución de indicadores"
    )

    df = df_historico.copy()


    # --------------------------------------------------
    # CONVERSIÓN DE HORAS
    # --------------------------------------------------

    df["hora_ingreso"] = pd.to_datetime(
        df["hora_ingreso"],
        format="%H:%M",
        errors="coerce"
    )

    df["hora_egreso"] = pd.to_datetime(
        df["hora_egreso"],
        format="%H:%M",
        errors="coerce"
    )


    # --------------------------------------------------
    # PERMANENCIA
    # --------------------------------------------------

    df["permanencia_minutos"] = (
        df["hora_egreso"]
        - df["hora_ingreso"]
    ) / pd.Timedelta(minutes=1)


    permanencia_anual = (
        df
        .dropna(
            subset=[
                "permanencia_minutos"
            ]
        )
        .groupby("anio")[
            "permanencia_minutos"
        ]
        .mean()
        .reset_index()
        .sort_values("anio")
    )


    # --------------------------------------------------
    # ERROR QR
    # --------------------------------------------------

    df_qr = df[
        df["estado_qr"].isin(
            [
                "Correcto",
                "Error"
            ]
        )
    ].copy()


    qr_anual = (
        df_qr
        .groupby("anio")
        .agg(
            lecturas=(
                "estado_qr",
                "count"
            ),
            errores=(
                "estado_qr",
                lambda x: (
                    x == "Error"
                ).sum()
            )
        )
        .reset_index()
        .sort_values("anio")
    )


    qr_anual["tasa_error"] = (
        qr_anual["errores"]
        / qr_anual["lecturas"]
    ) * 100


    # --------------------------------------------------
    # OCUPACIÓN
    # --------------------------------------------------

    df_ocupacion = df[
        df["capacidad_aula"] > 0
    ].copy()


    ocupacion_actividad = (
        df_ocupacion
        .groupby(
            [
                "anio",
                "actividad",
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


    ocupacion_actividad[
        "ocupacion_porcentaje"
    ] = (
        ocupacion_actividad[
            "participantes"
        ]
        / ocupacion_actividad[
            "capacidad_aula"
        ]
    ) * 100


    ocupacion_anual = (
        ocupacion_actividad
        .groupby("anio")[
            "ocupacion_porcentaje"
        ]
        .mean()
        .reset_index()
        .sort_values("anio")
    )


    # --------------------------------------------------
    # GRÁFICOS
    # --------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        st.markdown(
            "#### Permanencia promedio"
        )

        fig_permanencia = px.line(
            permanencia_anual,
            x="anio",
            y="permanencia_minutos",
            markers=True,
            text="permanencia_minutos"
        )

        fig_permanencia.update_traces(
            texttemplate="%{text:.0f} min",
            textposition="top center"
        )

        fig_permanencia.update_layout(
            xaxis_title="",
            yaxis_title="Minutos",
            xaxis=dict(
                tickmode="linear",
                dtick=1
            )
        )

        st.plotly_chart(
            fig_permanencia,
            use_container_width=True,
            key="grafico_historico_permanencia"
        )


    with col2:

        st.markdown(
            "#### Tasa de error QR"
        )

        fig_qr = px.line(
            qr_anual,
            x="anio",
            y="tasa_error",
            markers=True,
            text="tasa_error"
        )

        fig_qr.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="top center"
        )

        fig_qr.update_layout(
            xaxis_title="",
            yaxis_title="Error (%)",
            xaxis=dict(
                tickmode="linear",
                dtick=1
            )
        )

        st.plotly_chart(
            fig_qr,
            use_container_width=True,
            key="grafico_historico_qr"
        )


    with col3:

        st.markdown(
            "#### Ocupación promedio"
        )

        fig_ocupacion = px.line(
            ocupacion_anual,
            x="anio",
            y="ocupacion_porcentaje",
            markers=True,
            text="ocupacion_porcentaje"
        )

        fig_ocupacion.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="top center"
        )

        fig_ocupacion.update_layout(
            xaxis_title="",
            yaxis_title="Ocupación (%)",
            xaxis=dict(
                tickmode="linear",
                dtick=1
            )
        )

        st.plotly_chart(
            fig_ocupacion,
            use_container_width=True,
            key="grafico_historico_ocupacion"
        )