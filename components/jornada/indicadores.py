import streamlit as st


def mostrar_indicadores(df):


    # ----------------------------------------------
    # PARTICIPANTES ÚNICOS
    # ----------------------------------------------

    total_personas = (
        df["documento"]
        .nunique()
    )


    # ----------------------------------------------
    # INSCRIPCIONES
    # ----------------------------------------------

    total_inscripciones = len(df)


    # ----------------------------------------------
    # ASISTENCIA
    # ----------------------------------------------

    total_asistieron = int(
        df["asistio"].sum()
    )

    tasa_asistencia = (
        total_asistieron
        / total_inscripciones
    ) * 100


    # ----------------------------------------------
    # MIEMBROS UNLA
    # ----------------------------------------------

    porcentaje_unla = (
        df["Miembro UNLa"]
        .eq("Si")
        .mean()
    ) * 100


    # ----------------------------------------------
    # INDICADORES
    # ----------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Personas inscriptas",
            total_personas
        )

    with col2:
        st.metric(
            "Inscripciones",
            total_inscripciones
        )

    with col3:
        st.metric(
            "Tasa de asistencia",
            f"{tasa_asistencia:.1f}%"
        )

    with col4:
        st.metric(
            "Miembros UNLa",
            f"{porcentaje_unla:.1f}%"
        )
