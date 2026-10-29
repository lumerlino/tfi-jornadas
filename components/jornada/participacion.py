import streamlit as st
import plotly.express as px

from utils.limpieza_datos import (
    detectar_columnas_asistencia,
    construir_asistencia_larga
)

from components.jornada.participacion_perfil import (
    mostrar_perfil_participantes,
)

from components.jornada.participacion_asistencia import (
    mostrar_asistencia_participacion,
)

from components.jornada.participacion_analisis import (
    mostrar_analisis_participacion,
)

def mostrar_participacion(df):

    st.subheader("Participación en la jornada")


    # --------------------------------------------------
    # PERFIL DE PARTICIPANTES
    # --------------------------------------------------

    df_participantes = (
        df
        .drop_duplicates(subset="documento")
        .copy()
    )

    mostrar_perfil_participantes(df_participantes)

    # --------------------------------------------------
    # ASISTENCIA POR DÍA
    # --------------------------------------------------

    mostrar_asistencia_participacion(df)

    # --------------------------------------------------
    # ANÁLISIS DINÁMICO
    # --------------------------------------------------

    mostrar_analisis_participacion(df)
