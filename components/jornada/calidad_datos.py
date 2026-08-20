import streamlit as st

from utils.calidad_datos import obtener_mascaras_calidad


def mostrar_calidad_datos(df):

    st.subheader("Calidad de los datos")

    total_registros = len(df)

    mascaras = obtener_mascaras_calidad(df)


    # --------------------------------------------------
    # COLUMNAS ORIGINALES DEL ARCHIVO
    # --------------------------------------------------

    columnas_origen = [
        "id_participante",
        "tipo_participante",
        "carrera",
        "institucion",
        "actividad",
        "tipo_actividad",
        "tematica",
        "aula",
        "capacidad_aula",
        "estado_qr",
        "punto_acceso",
        "fecha",
        "hora_inicio_actividad",
        "hora_fin_actividad",
        "hora_ingreso",
        "hora_egreso",
        "inscripto",
        "asistio"
    ]


    # --------------------------------------------------
    # VALORES FALTANTES
    # --------------------------------------------------

    total_faltantes = (
        df[columnas_origen]
        .isna()
        .sum()
        .sum()
    )

    columnas_con_faltantes = (
        df[columnas_origen]
        .isna()
        .sum()
        .loc[lambda x: x > 0]
    )


    # --------------------------------------------------
    # DUPLICADOS
    # --------------------------------------------------

    filas_duplicadas = (
        df.duplicated().sum()
    )

    participaciones_duplicadas = (
        df.duplicated(
            subset=[
                "id_participante",
                "actividad"
            ]
        ).sum()
    )


    # --------------------------------------------------
    # VALIDACIONES ESPECÍFICAS
    # --------------------------------------------------

    ids_faltantes = (
        df["id_participante"]
        .isna()
        .sum()
    )

    horas_ingreso_faltantes = (
        df["hora_ingreso"]
        .isna()
        .sum()
    )

    horas_egreso_faltantes = (
        df["hora_egreso"]
        .isna()
        .sum()
    )

    egresos_anteriores_ingreso = (
        df[
            df["hora_egreso"]
            < df["hora_ingreso"]
        ]
        .shape[0]
    )

    capacidades_invalidas = (
        df[
            df["capacidad_aula"] <= 0
        ]
        .shape[0]
    )

    estados_qr_validos = [
        "Correcto",
        "Error"
    ]

    estados_qr_invalidos = (
        df[
            ~df["estado_qr"]
            .isin(estados_qr_validos)
        ]
        .shape[0]
    )


    # --------------------------------------------------
    # REGISTROS PROBLEMÁTICOS
    # --------------------------------------------------

    problemas = (
        df["id_participante"].isna()
        |
        df["hora_ingreso"].isna()
        |
        df["hora_egreso"].isna()
        |
        (df["hora_egreso"] < df["hora_ingreso"])
        |
        (df["capacidad_aula"] <= 0)
        |
        (~df["estado_qr"].isin(estados_qr_validos))
        |
        df.duplicated(
            subset=[
                "id_participante",
                "actividad"
            ]
        )
    )

    registros_problematicos = (
        problemas.sum()
    )

    registros_sin_problemas = (
        total_registros
        - registros_problematicos
    )

    porcentaje_sin_problemas = (
        registros_sin_problemas
        / total_registros
    ) * 100


    # --------------------------------------------------
    # INDICADORES GENERALES
    # --------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Registros procesados",
            total_registros
        )

    with col2:
        st.metric(
            "Registros con problemas",
            registros_problematicos
        )

    with col3:
        st.metric(
            "Valores faltantes",
            total_faltantes
        )

    with col4:
        st.metric(
            "Registros sin problemas detectados",
            f"{porcentaje_sin_problemas:.1f}%"
        )


    st.divider()


    # --------------------------------------------------
    # REGISTROS UTILIZABLES POR ANÁLISIS
    # --------------------------------------------------

    registros_participacion = (
        mascaras["participacion"].sum()
    )

    registros_personas = (
        mascaras["persona_unica"].sum()
    )

    registros_permanencia = (
        mascaras["permanencia"].sum()
    )

    registros_qr = (
        mascaras["qr"].sum()
    )

    registros_ocupacion = (
        mascaras["ocupacion"].sum()
    )


    st.markdown(
        "#### Registros utilizables por tipo de análisis"
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Participación",
            f"{registros_participacion / total_registros * 100:.1f}%"
        )

    with col2:
        st.metric(
            "Personas únicas",
            f"{registros_personas / total_registros * 100:.1f}%"
        )

    with col3:
        st.metric(
            "Permanencia",
            f"{registros_permanencia / total_registros * 100:.1f}%"
        )

    with col4:
        st.metric(
            "Análisis QR",
            f"{registros_qr / total_registros * 100:.1f}%"
        )

    with col5:
        st.metric(
            "Ocupación",
            f"{registros_ocupacion / total_registros * 100:.1f}%"
        )


    st.caption(
        "Un registro puede ser válido para un tipo de análisis "
        "y no serlo para otro."
    )


    st.divider()


    # --------------------------------------------------
    # RESUMEN COMPACTO
    # --------------------------------------------------

    st.markdown(
        "#### Resumen de validaciones"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write("**Identificación**")

        if ids_faltantes == 0:
            st.success("Sin problemas")
        else:
            st.warning(
                f"{ids_faltantes} registros sin ID"
            )

        st.write("**Horarios**")

        total_horarios_faltantes = (
            horas_ingreso_faltantes
            + horas_egreso_faltantes
        )

        if total_horarios_faltantes == 0:
            st.success("Sin problemas")
        else:
            st.warning(
                f"{total_horarios_faltantes} horarios faltantes"
            )


    with col2:

        st.write("**Participaciones duplicadas**")

        if participaciones_duplicadas == 0:
            st.success("Sin problemas")
        else:
            st.warning(
                f"{participaciones_duplicadas} posibles duplicados"
            )

        st.write("**Capacidad de aulas**")

        if capacidades_invalidas == 0:
            st.success("Sin problemas")
        else:
            st.warning(
                f"{capacidades_invalidas} valores inválidos"
            )


    with col3:

        st.write("**Estado QR**")

        if estados_qr_invalidos == 0:
            st.success("Sin problemas")
        else:
            st.warning(
                f"{estados_qr_invalidos} valores inválidos"
            )

        st.write("**Orden ingreso / egreso**")

        if egresos_anteriores_ingreso == 0:
            st.success("Sin problemas")
        else:
            st.warning(
                f"{egresos_anteriores_ingreso} inconsistencias"
            )


    # --------------------------------------------------
    # DETALLE DESPLEGABLE
    # --------------------------------------------------

    with st.expander(
        "Ver detalle de las validaciones"
    ):

        st.markdown("##### Identificadores")

        if ids_faltantes == 0:
            st.success(
                "No se detectaron identificadores faltantes."
            )
        else:
            st.warning(
                f"Se encontraron {ids_faltantes} registros "
                f"sin identificador de participante."
            )


        st.markdown("##### Horarios")

        if horas_ingreso_faltantes == 0 and horas_egreso_faltantes == 0:

            st.success(
                "No se detectaron horarios faltantes."
            )

        else:

            st.warning(
                f"Horarios faltantes: "
                f"{horas_ingreso_faltantes} ingresos y "
                f"{horas_egreso_faltantes} egresos."
            )


        if egresos_anteriores_ingreso == 0:

            st.success(
                "No se detectaron egresos anteriores al ingreso."
            )

        else:

            st.warning(
                f"Se encontraron {egresos_anteriores_ingreso} "
                f"registros con egreso anterior al ingreso."
            )


        st.markdown("##### Participaciones duplicadas")

        if participaciones_duplicadas == 0:

            st.success(
                "No se detectaron participaciones duplicadas."
            )

        else:

            st.warning(
                f"Se encontraron {participaciones_duplicadas} "
                f"posibles participaciones duplicadas."
            )


        st.markdown("##### Capacidad de aulas")

        if capacidades_invalidas == 0:

            st.success(
                "Todas las capacidades de aula son válidas."
            )

        else:

            st.warning(
                f"Se encontraron {capacidades_invalidas} "
                f"registros con capacidades inválidas."
            )


        st.markdown("##### Estado QR")

        if estados_qr_invalidos == 0:

            st.success(
                "Todos los estados QR son válidos."
            )

        else:

            st.warning(
                f"Se encontraron {estados_qr_invalidos} "
                f"registros con estados QR inválidos."
            )


        if len(columnas_con_faltantes) > 0:

            st.divider()

            st.markdown(
                "##### Valores faltantes por columna"
            )

            detalle_faltantes = (
                columnas_con_faltantes
                .reset_index()
            )

            detalle_faltantes.columns = [
                "Columna",
                "Valores faltantes"
            ]

            st.dataframe(
                detalle_faltantes,
                use_container_width=True
            )


        if filas_duplicadas > 0:

            st.divider()

            st.markdown(
                "##### Filas completamente duplicadas"
            )

            st.write(
                f"Se detectaron {filas_duplicadas} "
                f"filas completamente duplicadas."
            )