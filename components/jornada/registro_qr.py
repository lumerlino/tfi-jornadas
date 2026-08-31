# --------------------------------------------------
# Desconectado a propósito de views/analizar_jornada.py: el
# esquema real de inscripción trae el código QR asignado a cada
# persona, pero no un log de lecturas (con timestamp, punto de
# acceso, éxito/error), así que no hay nada que calcular. Si el
# sistema de origen alguna vez registra ese log, se puede
# reactivar agregando la pestaña de vuelta en
# views/analizar_jornada.py. La lógica de análisis original (tasa
# de error por punto de acceso y franja horaria) quedó en el
# historial de git de este archivo, de antes del refactor al
# esquema real.
# --------------------------------------------------

import streamlit as st


def mostrar_registro_qr(df):

    st.subheader("Calidad de los registros QR")

    st.info(
        "Este análisis no está disponible para este tipo de "
        "archivo: el registro de inscripción incluye el código QR "
        "de cada persona, pero no un log de lecturas por punto de "
        "acceso ni su estado."
    )
