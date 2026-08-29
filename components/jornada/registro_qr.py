import streamlit as st


def mostrar_registro_qr(df):

    st.subheader("Calidad de los registros QR")

    st.info(
        "Este análisis no está disponible para este tipo de "
        "archivo: el registro de inscripción incluye el código QR "
        "de cada persona, pero no un log de lecturas por punto de "
        "acceso ni su estado."
    )
