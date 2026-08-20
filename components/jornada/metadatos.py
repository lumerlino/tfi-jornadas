import streamlit as st
from datetime import date


def mostrar_metadatos_jornada():

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