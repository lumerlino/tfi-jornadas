import streamlit as st
import plotly.express as px

from utils.calidad_datos import obtener_mascaras_calidad


def mostrar_registro_qr(df):

    st.subheader("Calidad de los registros QR")

    mascaras = obtener_mascaras_calidad(df)

    df_qr = df[
        mascaras["qr"]
    ].copy()


    if len(df_qr) == 0:

        st.warning(
            "No hay registros válidos suficientes "
            "para analizar las lecturas QR."
        )

        return


    # --------------------------------------------------
    # INDICADORES PRINCIPALES
    # --------------------------------------------------

    total_lecturas = len(df_qr)

    total_correctas = len(
        df_qr[
            df_qr["estado_qr"] == "Correcto"
        ]
    )

    total_errores = len(
        df_qr[
            df_qr["estado_qr"] == "Error"
        ]
    )

    tasa_error = (
        total_errores
        / total_lecturas
    ) * 100


    col1, col2, col3, col4 = st.columns(4)


    with col1:
        st.metric(
            "Lecturas analizadas",
            total_lecturas
        )


    with col2:
        st.metric(
            "Lecturas correctas",
            total_correctas
        )


    with col3:
        st.metric(
            "Errores detectados",
            total_errores
        )


    with col4:
        st.metric(
            "Tasa de error",
            f"{tasa_error:.1f}%"
        )


    st.divider()


    # --------------------------------------------------
    # ESTADO GENERAL
    # --------------------------------------------------

    resumen_qr = (
        df_qr["estado_qr"]
        .value_counts()
        .reset_index()
    )

    resumen_qr.columns = [
        "estado",
        "cantidad"
    ]


    # --------------------------------------------------
    # ERRORES POR PUNTO DE ACCESO
    # --------------------------------------------------

    errores_por_acceso = (
        df_qr[
            df_qr["estado_qr"] == "Error"
        ]
        .groupby("punto_acceso")
        .size()
        .reset_index(
            name="errores"
        )
        .sort_values(
            "errores",
            ascending=False
        )
    )


    col1, col2 = st.columns([1, 2])


    with col1:

        st.markdown(
            "#### Estado de las lecturas"
        )

        fig_qr = px.pie(
            resumen_qr,
            names="estado",
            values="cantidad",
            hole=0.5
        )

        st.plotly_chart(
            fig_qr,
            use_container_width=True,
            key="grafico_estado_qr"
        )


    with col2:

        st.markdown(
            "#### Errores por punto de acceso"
        )

        if len(errores_por_acceso) > 0:

            fig_error_acceso = px.bar(
                errores_por_acceso,
                x="punto_acceso",
                y="errores",
                text="errores"
            )

            fig_error_acceso.update_layout(
                xaxis_title="",
                yaxis_title="Errores"
            )

            st.plotly_chart(
                fig_error_acceso,
                use_container_width=True,
                key="grafico_errores_acceso"
            )

        else:

            st.success(
                "No se detectaron errores QR "
                "en los registros seleccionados."
            )


    # --------------------------------------------------
    # TASA DE ERROR POR DÍA
    # --------------------------------------------------

    errores_fecha = (
        df_qr
        .groupby(
            [
                "fecha",
                "fecha_texto"
            ]
        )
        .agg(
            registros=(
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
        .sort_values("fecha")
    )


    errores_fecha["tasa_error"] = (
        errores_fecha["errores"]
        / errores_fecha["registros"]
    ) * 100


    # --------------------------------------------------
    # ERRORES POR FRANJA HORARIA
    # --------------------------------------------------

    df_qr["hora_ingreso_num"] = (
        df_qr["hora_ingreso"]
        .dt.hour
    )

    df_qr["franja_horaria"] = (
        df_qr["hora_ingreso_num"]
        .astype(str)
        .str.zfill(2)
        + ":00 - "
        + df_qr["hora_ingreso_num"]
        .astype(str)
        .str.zfill(2)
        + ":59"
    )


    errores_hora = (
        df_qr[
            df_qr["estado_qr"] == "Error"
        ]
        .groupby(
            [
                "hora_ingreso_num",
                "franja_horaria"
            ]
        )
        .size()
        .reset_index(
            name="errores"
        )
        .sort_values(
            "hora_ingreso_num"
        )
    )


    col1, col2 = st.columns(2)


    with col1:

        st.markdown(
            "#### Tasa de error por día"
        )

        fig_error_fecha = px.line(
            errores_fecha,
            x="fecha_texto",
            y="tasa_error",
            markers=True,
            text="tasa_error"
        )

        fig_error_fecha.update_traces(
            texttemplate="%{text:.1f}%"
        )

        fig_error_fecha.update_layout(
            xaxis_title="Fecha",
            yaxis_title="Tasa de error (%)"
        )

        st.plotly_chart(
            fig_error_fecha,
            use_container_width=True,
            key="grafico_tasa_error_fecha"
        )


    with col2:

        st.markdown(
            "#### Errores por franja horaria"
        )

        if len(errores_hora) > 0:

            fig_error_hora = px.bar(
                errores_hora,
                x="franja_horaria",
                y="errores",
                text="errores"
            )

            fig_error_hora.update_layout(
                xaxis_title="Franja horaria",
                yaxis_title="Errores"
            )

            st.plotly_chart(
                fig_error_hora,
                use_container_width=True,
                key="grafico_errores_hora"
            )

        else:

            st.success(
                "No se detectaron errores QR "
                "para analizar por horario."
            )


    # --------------------------------------------------
    # PUNTO DE ACCESO A REVISAR
    # --------------------------------------------------

    st.markdown(
        "#### Puntos de acceso a revisar"
    )


    if total_errores == 0:

        st.success(
            "No se detectaron errores QR."
        )

    else:

        resumen_acceso = (
            df_qr
            .groupby("punto_acceso")
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
        )


        resumen_acceso["tasa_error"] = (
            resumen_acceso["errores"]
            / resumen_acceso["lecturas"]
        ) * 100


        resumen_acceso = (
            resumen_acceso
            .sort_values(
                "tasa_error",
                ascending=False
            )
        )


        peor_acceso = (
            resumen_acceso.iloc[0]
        )


        st.warning(
            f"El punto de acceso con mayor tasa de error es "
            f"**{peor_acceso['punto_acceso']}**, con "
            f"{peor_acceso['tasa_error']:.1f}% "
            f"({int(peor_acceso['errores'])} errores sobre "
            f"{int(peor_acceso['lecturas'])} lecturas)."
        )


    # --------------------------------------------------
    # DETALLE
    # --------------------------------------------------

    with st.expander(
        "Ver detalle de errores QR"
    ):

        if total_errores == 0:

            st.write(
                "No hay errores para mostrar."
            )

        else:

            errores_detalle = (
                df_qr[
                    df_qr["estado_qr"] == "Error"
                ][
                    [
                        "id_participante",
                        "fecha_texto",
                        "actividad",
                        "hora_ingreso",
                        "punto_acceso"
                    ]
                ]
                .copy()
            )


            errores_detalle[
                "hora_ingreso"
            ] = (
                errores_detalle[
                    "hora_ingreso"
                ]
                .dt.strftime("%H:%M")
            )


            errores_detalle = (
                errores_detalle
                .rename(
                    columns={
                        "id_participante": "Participante",
                        "fecha_texto": "Fecha",
                        "actividad": "Actividad",
                        "hora_ingreso": "Hora",
                        "punto_acceso": "Punto de acceso"
                    }
                )
            )


            st.dataframe(
                errores_detalle,
                use_container_width=True,
                hide_index=True
            )