import streamlit as st


def mostrar_indicadores_historicos(df_historico):

    resumen_anual = (
        df_historico
        .groupby("anio")
        .agg(
            participaciones=(
                "id_participante",
                "size"
            ),
            participantes_unicos=(
                "id_participante",
                "nunique"
            )
        )
        .reset_index()
        .sort_values("anio")
    )


    if len(resumen_anual) == 0:
        return


    # --------------------------------------------------
    # ÚLTIMA JORNADA
    # --------------------------------------------------

    ultima_jornada = (
        resumen_anual.iloc[-1]
    )


    st.markdown(
        "### Última jornada"
    )

    st.caption(
        f"Jornada {int(ultima_jornada['anio'])}"
    )


    # --------------------------------------------------
    # SI SOLO HAY UN AÑO
    # --------------------------------------------------

    if len(resumen_anual) == 1:

        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "Participantes únicos",
                int(
                    ultima_jornada[
                        "participantes_unicos"
                    ]
                )
            )


        with col2:

            st.metric(
                "Participaciones",
                int(
                    ultima_jornada[
                        "participaciones"
                    ]
                )
            )


        st.info(
            "Se necesita al menos otra jornada "
            "para calcular variaciones históricas."
        )

        return


    # --------------------------------------------------
    # JORNADA ANTERIOR
    # --------------------------------------------------

    jornada_anterior = (
        resumen_anual.iloc[-2]
    )


    # --------------------------------------------------
    # VARIACIÓN DE PARTICIPANTES
    # --------------------------------------------------

    participantes_anteriores = (
        jornada_anterior[
            "participantes_unicos"
        ]
    )


    if participantes_anteriores > 0:

        variacion_participantes = (
            (
                ultima_jornada[
                    "participantes_unicos"
                ]
                - participantes_anteriores
            )
            / participantes_anteriores
        ) * 100

    else:

        variacion_participantes = 0


    # --------------------------------------------------
    # VARIACIÓN DE PARTICIPACIONES
    # --------------------------------------------------

    participaciones_anteriores = (
        jornada_anterior[
            "participaciones"
        ]
    )


    if participaciones_anteriores > 0:

        variacion_participaciones = (
            (
                ultima_jornada[
                    "participaciones"
                ]
                - participaciones_anteriores
            )
            / participaciones_anteriores
        ) * 100

    else:

        variacion_participaciones = 0


    # --------------------------------------------------
    # INDICADORES
    # --------------------------------------------------

    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Participantes únicos",
            int(
                ultima_jornada[
                    "participantes_unicos"
                ]
            ),
            delta=(
                f"{variacion_participantes:+.1f}% "
                f"vs {int(jornada_anterior['anio'])}"
            )
        )


    with col2:

        st.metric(
            "Participaciones",
            int(
                ultima_jornada[
                    "participaciones"
                ]
            ),
            delta=(
                f"{variacion_participaciones:+.1f}% "
                f"vs {int(jornada_anterior['anio'])}"
            )
        )