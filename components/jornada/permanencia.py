# --------------------------------------------------
# Desconectado a propósito de views/analizar_jornada.py: el
# esquema real de inscripción no trae hora_ingreso/hora_egreso
# por actividad, así que no hay nada que calcular. Si el sistema
# de origen alguna vez registra eso, se puede reactivar agregando
# la pestaña de vuelta en views/analizar_jornada.py. La lógica de
# análisis original (rangos de permanencia, retiro anticipado por
# actividad) quedó en el historial de git de este archivo, de
# antes del refactor al esquema real.
# --------------------------------------------------

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
