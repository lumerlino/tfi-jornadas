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
        "Nombre/s",
        "Apellido/s",
        "documento",
        "mail",
        "Miembro UNLa",
        "Rol principal",
        "Otro Rol principal",
        "Investigador Carreras",
        "Otro Investigador Carreras",
        "Tipo inscripción",
        "Source",
        "IsWelcomeMailSent",
        "QRCode",
        "isPresent_original",
        "IsAssistanceCertifySent"
    ]

    columnas_origen = [
        columna
        for columna in columnas_origen
        if columna in df.columns
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
    # DUPLICADOS Y VALIDACIONES ESPECÍFICAS
    # --------------------------------------------------

    filas_duplicadas = df.duplicated().sum()

    documentos_duplicados = (
        (~mascaras["documento_unico"]).sum()
    )

    documentos_faltantes = (
        (~mascaras["documento_valido"]).sum()
    )

    mails_invalidos = (
        (~mascaras["mail_valido"]).sum()
    )

    inconsistencias_asistencia = (
        (~mascaras["asistencia_coherente"]).sum()
    )


    # --------------------------------------------------
    # REGISTROS PROBLEMÁTICOS
    # --------------------------------------------------

    problemas = (
        (~mascaras["documento_valido"])
        | (~mascaras["documento_unico"])
        | (~mascaras["mail_valido"])
        | (~mascaras["datos_completos"])
    )

    registros_problematicos = problemas.sum()

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
    # REGISTROS UTILIZABLES POR TIPO DE VALIDACIÓN
    # --------------------------------------------------

    st.markdown(
        "#### Registros que pasan cada validación"
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Documento",
            f"{mascaras['documento_valido'].mean() * 100:.1f}%"
        )

    with col2:
        st.metric(
            "Documento único",
            f"{mascaras['documento_unico'].mean() * 100:.1f}%"
        )

    with col3:
        st.metric(
            "Mail",
            f"{mascaras['mail_valido'].mean() * 100:.1f}%"
        )

    with col4:
        st.metric(
            "Datos completos",
            f"{mascaras['datos_completos'].mean() * 100:.1f}%"
        )

    with col5:
        st.metric(
            "Asistencia coherente",
            f"{mascaras['asistencia_coherente'].mean() * 100:.1f}%"
        )

    st.caption(
        "Un registro puede fallar una validación "
        "y ser válido para las demás."
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

        st.write("**Documento**")

        if documentos_faltantes == 0:
            st.success("Sin problemas")
        else:
            st.warning(
                f"{documentos_faltantes} registros sin documento"
            )

        st.write("**Documentos duplicados**")

        if documentos_duplicados == 0:
            st.success("Sin problemas")
        else:
            st.warning(
                f"{documentos_duplicados} registros con "
                f"documento repetido"
            )


    with col2:

        st.write("**Mail**")

        if mails_invalidos == 0:
            st.success("Sin problemas")
        else:
            st.warning(
                f"{mails_invalidos} mails con formato inválido"
            )

        st.write("**Filas completamente duplicadas**")

        if filas_duplicadas == 0:
            st.success("Sin problemas")
        else:
            st.warning(
                f"{filas_duplicadas} filas duplicadas"
            )


    with col3:

        st.write("**Asistencia vs. isPresent original**")

        if inconsistencias_asistencia == 0:
            st.success("Sin problemas")
        else:
            st.warning(
                f"{inconsistencias_asistencia} registros donde "
                f"'isPresent' no coincide con la asistencia por día"
            )


    # --------------------------------------------------
    # DETALLE DESPLEGABLE
    # --------------------------------------------------

    with st.expander(
        "Ver detalle de las validaciones"
    ):

        st.markdown("##### Inconsistencia de asistencia")

        st.write(
            "La columna `isPresent` original del archivo puede "
            "no coincidir con lo que indican las columnas "
            "`Asistencia YYYY-MM-DD` día por día. Se conservó el "
            "valor original en `isPresent_original` y se calculó "
            "`asistio` a partir de la asistencia diaria, que es la "
            "fuente utilizada en el resto del análisis."
        )

        if inconsistencias_asistencia == 0:

            st.success(
                "No se detectaron inconsistencias."
            )

        else:

            st.warning(
                f"Se encontraron {inconsistencias_asistencia} "
                f"registros con 'isPresent' distinto de la "
                f"asistencia derivada."
            )

            st.dataframe(
                df[~mascaras["asistencia_coherente"]][
                    [
                        "documento",
                        "Nombre/s",
                        "Apellido/s",
                        "isPresent_original",
                        "asistio"
                    ]
                ],
                use_container_width=True,
                hide_index=True
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


        if documentos_duplicados > 0:

            st.divider()

            st.markdown(
                "##### Documentos duplicados"
            )

            st.dataframe(
                df[~mascaras["documento_unico"]]
                .sort_values("documento")
                [
                    [
                        "documento",
                        "Nombre/s",
                        "Apellido/s",
                        "mail"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )
