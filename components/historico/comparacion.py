import streamlit as st
import pandas as pd


def calcular_metricas_jornada(df):

    participantes_unicos = (
        df["id_participante"]
        .nunique()
    )

    participaciones = len(df)


    # --------------------------------------------------
    # PERMANENCIA PROMEDIO
    # --------------------------------------------------

    df_tiempos = df.copy()

    df_tiempos["hora_ingreso"] = pd.to_datetime(
        df_tiempos["hora_ingreso"],
        format="%H:%M",
        errors="coerce"
    )

    df_tiempos["hora_egreso"] = pd.to_datetime(
        df_tiempos["hora_egreso"],
        format="%H:%M",
        errors="coerce"
    )

    df_tiempos["permanencia_minutos"] = (
        df_tiempos["hora_egreso"]
        - df_tiempos["hora_ingreso"]
    ) / pd.Timedelta(minutes=1)


    permanencia_promedio = (
        df_tiempos[
            "permanencia_minutos"
        ]
        .dropna()
        .mean()
    )


    # --------------------------------------------------
    # TASA DE ERROR QR
    # --------------------------------------------------

    df_qr = df[
        df["estado_qr"].isin(
            [
                "Correcto",
                "Error"
            ]
        )
    ]


    if len(df_qr) > 0:

        errores = (
            df_qr["estado_qr"]
            == "Error"
        ).sum()

        tasa_error_qr = (
            errores
            / len(df_qr)
        ) * 100

    else:

        tasa_error_qr = 0


    # --------------------------------------------------
    # OCUPACIÓN PROMEDIO
    # --------------------------------------------------

    df_ocupacion = df[
        df["capacidad_aula"] > 0
    ]


    ocupacion_actividad = (
        df_ocupacion
        .groupby(
            [
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


    ocupacion_promedio = (
        ocupacion_actividad[
            "ocupacion_porcentaje"
        ]
        .mean()
    )


    return {
        "Participantes únicos": participantes_unicos,
        "Participaciones": participaciones,
        "Permanencia promedio": permanencia_promedio,
        "Tasa de error QR": tasa_error_qr,
        "Ocupación promedio": ocupacion_promedio
    }


def mostrar_comparacion_historica(df_historico):

    st.markdown(
        "### Comparar jornadas"
    )


    # --------------------------------------------------
    # AÑOS DISPONIBLES
    # --------------------------------------------------

    anios = sorted(
        df_historico["anio"]
        .dropna()
        .unique()
        .tolist()
    )


    if len(anios) < 2:

        st.info(
            "Se necesitan al menos dos jornadas "
            "para realizar una comparación."
        )

        return


    # --------------------------------------------------
    # SELECTORES
    # --------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        anio_a = st.selectbox(
            "Jornada A",
            anios,
            index=0,
            key="comparacion_anio_a"
        )


    with col2:

        anio_b = st.selectbox(
            "Jornada B",
            anios,
            index=len(anios) - 1,
            key="comparacion_anio_b"
        )


    if anio_a == anio_b:

        st.warning(
            "Seleccioná dos años diferentes "
            "para realizar la comparación."
        )

        return


    # --------------------------------------------------
    # FILTRAMOS LOS DATOS
    # --------------------------------------------------

    df_a = df_historico[
        df_historico["anio"] == anio_a
    ]

    df_b = df_historico[
        df_historico["anio"] == anio_b
    ]


    metricas_a = calcular_metricas_jornada(
        df_a
    )

    metricas_b = calcular_metricas_jornada(
        df_b
    )


    # --------------------------------------------------
    # TABLA DE COMPARACIÓN
    # --------------------------------------------------

    comparacion = []


    for indicador in metricas_a:

        valor_a = metricas_a[
            indicador
        ]

        valor_b = metricas_b[
            indicador
        ]


        if indicador in [
            "Participantes únicos",
            "Participaciones",
            "Permanencia promedio"
        ]:

            if valor_a != 0:

                variacion = (
                    (
                        valor_b
                        - valor_a
                    )
                    / valor_a
                ) * 100

            else:

                variacion = 0


            variacion_texto = (
                f"{variacion:+.1f}%"
            )


        else:

            variacion = (
                valor_b
                - valor_a
            )

            variacion_texto = (
                f"{variacion:+.1f} pp"
            )


        comparacion.append(
            {
                "Indicador": indicador,
                str(anio_a): valor_a,
                str(anio_b): valor_b,
                "Variación": variacion_texto
            }
        )


    df_comparacion = pd.DataFrame(
        comparacion
    )


    # --------------------------------------------------
    # FORMATO DE VALORES
    # --------------------------------------------------

    def formatear_valor(
        indicador,
        valor
    ):

        if indicador in [
            "Participantes únicos",
            "Participaciones"
        ]:

            return str(
                int(valor)
            )


        elif indicador == "Permanencia promedio":

            if pd.isna(valor):
                return "-"

            return (
                f"{valor:.0f} min"
            )


        else:

            if pd.isna(valor):
                return "-"

            return (
                f"{valor:.1f}%"
            )


    df_comparacion[
        str(anio_a)
    ] = df_comparacion.apply(
        lambda fila:
        formatear_valor(
            fila["Indicador"],
            fila[str(anio_a)]
        ),
        axis=1
    )


    df_comparacion[
        str(anio_b)
    ] = df_comparacion.apply(
        lambda fila:
        formatear_valor(
            fila["Indicador"],
            fila[str(anio_b)]
        ),
        axis=1
    )


    st.dataframe(
        df_comparacion,
        use_container_width=True,
        hide_index=True
    )