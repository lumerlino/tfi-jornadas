import streamlit as st


def mostrar_ocupacion(df):

    st.subheader("Ocupación de aulas y actividades")

    st.info(
        "Este análisis no está disponible para este tipo de "
        "archivo: el registro de inscripción no incluye datos "
        "de actividades ni de aulas."
    )
