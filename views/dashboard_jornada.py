import streamlit as st

from utils.guardado_historico import COLUMNAS_PARTICIPACIONES
from utils.limpieza_datos import detectar_columnas_asistencia
from utils.ui_tabs import mostrar_tabs
from components.jornada.indicadores import mostrar_indicadores
from components.jornada.participacion import mostrar_participacion
from components.jornada.tabla_datos import mostrar_datos
from components.jornada.calidad_datos import mostrar_calidad_datos
from components.jornada.explorar import mostrar_explorar


def mostrar_dashboard_jornada(df, configuraciones):

    # --------------------------------------------------
    # VISTA DE ANÁLISIS: solo columnas oficiales + asistencia
    # + configuradas. Sirve tanto para un "df" recién limpiado de
    # un Excel como para uno reconstruido desde la base
    # (utils/jornada_guardada.py::reconstruir_jornada) — a este
    # punto ya están limpios los dos, esta función no le importa
    # de dónde vinieron.
    # --------------------------------------------------

    columnas_asistencia = detectar_columnas_asistencia(df)

    columnas_a_mantener = (
        set(COLUMNAS_PARTICIPACIONES.keys())
        | set(columnas_asistencia)
        | set(configuraciones.keys())
    )

    df_vista = df[
        [
            columna
            for columna in df.columns
            if columna in columnas_a_mantener
        ]
    ]


    # --------------------------------------------------
    # FILTROS
    # --------------------------------------------------

    df_filtrado = df_vista


    # --------------------------------------------------
    # INDICADORES
    # --------------------------------------------------

    st.subheader("Resumen de la jornada")

    mostrar_indicadores(
        df_filtrado
    )


    st.divider()


    # --------------------------------------------------
    # PESTAÑAS DEL DASHBOARD
    # --------------------------------------------------

    pestania = mostrar_tabs(
        [
            "👥 Participación",
            "🔎 Calidad de datos",
            "📈 Variables",
            "📋 Datos",
        ],
        key="dashboard_jornada_tab"
    )


    if pestania == "👥 Participación":

        mostrar_participacion(
            df_filtrado
        )


    elif pestania == "🔎 Calidad de datos":

        mostrar_calidad_datos(
            df_vista
        )


    elif pestania == "📈 Variables":

        mostrar_explorar(
            df_filtrado,
            configuraciones
        )

    elif pestania == "📋 Datos":

         mostrar_datos(
             df_filtrado
        )
