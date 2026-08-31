import streamlit as st
from datetime import date

from utils.limpieza_datos import detectar_columnas_asistencia


def inferir_fechas_desde_asistencia(df):

    columnas_asistencia = detectar_columnas_asistencia(df)

    if not columnas_asistencia:
        return None

    fechas = sorted(
        date.fromisoformat(
            columna.replace("Asistencia ", "")
        )
        for columna in columnas_asistencia
    )

    return fechas[0], fechas[-1]


def mostrar_metadatos_jornada(df=None):

    st.markdown(
        "### Datos generales de la jornada"
    )

    st.write(
        "Completá esta información para identificar la jornada que estás analizando. "
        "Estos datos se utilizarán para asociar el archivo cargado con el año correspondiente "
        "y permitir su consulta y comparación en el histórico."
    )


    # --------------------------------------------------
    # VALORES INICIALES
    # --------------------------------------------------

    metadatos_guardados = st.session_state.get(
        "metadatos_jornada"
    )


    if metadatos_guardados is not None:

        anio_inicial = (
            metadatos_guardados["anio"]
        )

        fecha_inicio_inicial = (
            metadatos_guardados["fecha_inicio"]
        )

        fecha_fin_inicial = (
            metadatos_guardados["fecha_fin"]
        )

    else:

        fechas_inferidas = (
            inferir_fechas_desde_asistencia(df)
            if df is not None
            else None
        )

        if fechas_inferidas is not None:

            fecha_inicio_inicial, fecha_fin_inicial = fechas_inferidas
            anio_inicial = fecha_inicio_inicial.year

            st.info(
                "Se detectaron columnas de asistencia por día en el "
                "archivo — se completaron el año y las fechas de "
                "inicio/fin automáticamente. Podés ajustarlas si "
                "hace falta."
            )

        else:

            anio_inicial = 2026
            fecha_inicio_inicial = date.today()
            fecha_fin_inicial = date.today()


    # --------------------------------------------------
    # FORMULARIO
    # --------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        anio = st.number_input(
            "Año de la jornada",
            min_value=2000,
            max_value=2100,
            step=1,
            value=int(anio_inicial)
        )


    with col2:

        fecha_inicio = st.date_input(
            "Fecha de inicio",
            value=fecha_inicio_inicial
        )


    with col3:

        fecha_fin = st.date_input(
            "Fecha de fin",
            value=fecha_fin_inicial
        )


    # --------------------------------------------------
    # RESULTADO
    # --------------------------------------------------

    metadatos = {
        "anio": int(anio),
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin
    }


    return metadatos