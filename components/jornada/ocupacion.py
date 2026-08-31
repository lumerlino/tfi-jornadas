# --------------------------------------------------
# Desconectado a propósito de views/analizar_jornada.py: el
# esquema real de inscripción no trae asignación de aula ni de
# actividad por persona, así que no hay nada que calcular. Si el
# sistema de origen alguna vez registra eso, se puede reactivar
# agregando la pestaña de vuelta en views/analizar_jornada.py. La
# lógica de análisis original (ocupación por actividad, capacidad
# vs. participantes) quedó en el historial de git de este archivo,
# de antes del refactor al esquema real.
# --------------------------------------------------

import streamlit as st


def mostrar_ocupacion(df):

    st.subheader("Ocupación de aulas y actividades")

    st.info(
        "Este análisis no está disponible para este tipo de "
        "archivo: el registro de inscripción no incluye datos "
        "de actividades ni de aulas."
    )
