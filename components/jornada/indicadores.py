import streamlit as st


def mostrar_indicadores(df):

    # ----------------------------------------------
    # INSCRIPCIONES
    # ----------------------------------------------

    total_inscripciones = len(df)


    # ----------------------------------------------
    # PARTICIPANTES ÚNICOS Y ASISTENCIA
    # ----------------------------------------------

    tiene_documento = "documento" in df.columns
    tiene_asistencia = "asistio" in df.columns

    total_personas = None
    total_asistieron = None
    tasa_asistencia = None

    if tiene_documento:

        documentos_validos = (
            df["documento"]
            .dropna()
            .astype(str)
            .str.strip()
        )

        documentos_validos = documentos_validos[
            documentos_validos.ne("")
            & documentos_validos.str.lower().ne("nan")
        ]

        total_personas = documentos_validos.nunique()

        if tiene_asistencia:

            asistencia_por_persona = (
                df[
                    df["documento"].notna()
                ]
                .groupby("documento")["asistio"]
                .any()
            )

            total_asistieron = int(
                asistencia_por_persona.sum()
            )

            if total_personas > 0:
                tasa_asistencia = (
                    total_asistieron
                    / total_personas
                ) * 100


    # ----------------------------------------------
    # INDICADORES
    # ----------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total de inscripciones",
            total_inscripciones
        )

    with col2:
        st.metric(
            "Participantes únicos",
            (
                total_personas
                if total_personas is not None
                else "No disponible"
            )
        )

    with col3:
        st.metric(
            "Asistieron",
            (
                total_asistieron
                if total_asistieron is not None
                else "No disponible"
            )
        )

    with col4:
        st.metric(
            "Tasa de asistencia",
            (
                f"{tasa_asistencia:.1f}%"
                if tasa_asistencia is not None
                else "No disponible"
            )
        )