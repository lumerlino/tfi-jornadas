import streamlit as st


def mostrar_permanencia(df):

    st.subheader(
        "Permanencia de los participantes"
    )

    st.info(
        "Este análisis no está disponible para este tipo de "
        "archivo: el registro de inscripción no incluye horarios "
        "de ingreso y egreso por actividad."
    )
