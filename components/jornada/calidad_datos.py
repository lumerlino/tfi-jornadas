import streamlit as st

from components.jornada.calidad_datos_calculos import calcular_calidad_datos
from components.jornada.calidad_datos_interpretacion import (
    mostrar_interpretacion_calidad,
)
from components.jornada.calidad_datos_detalle import (
    mostrar_detalle_validaciones,
)


def mostrar_calidad_datos(df):
    st.subheader("Calidad de los datos")

    datos = calcular_calidad_datos(df)

    # Indicadores generales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Registros procesados",
            datos["total_registros"]
        )

    with col2:
        st.metric(
            "Registros con problemas",
            datos["registros_problematicos"]
        )

    with col3:
        st.metric(
            "Reinscripciones",
            datos["reinscripciones"]
        )

    with col4:
        st.metric(
            "Registros sin problemas detectados",
            f"{datos['porcentaje_sin_problemas']:.1f}%"
        )

    st.divider()

    # Porcentaje de registros válidos
    st.markdown("#### Porcentaje de registros válidos")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Participantes con número de documento cargado",
            f"{datos['mascaras']['documento_valido'].mean() * 100:.1f}%"
        )

    with col2:
        st.metric(
            "Participantes con correo con formato válido",
            f"{datos['mascaras']['mail_valido'].mean() * 100:.1f}%"
        )

    with col3:
        st.metric(
            "Participantes con Rol principal cargado",
            f"{datos['rol_informado'].mean() * 100:.1f}%"
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            "Participantes con Tipo de inscripción cargado",
            f"{datos['tipo_inscripcion_informado'].mean() * 100:.1f}%"
        )

    with col5:
        st.metric(
            "Mail de bienvenida enviado",
            (
                f"{datos['welcome_mail_enviado']:.1f}%"
                if datos["welcome_mail_enviado"] is not None
                else "No disponible"
            )
        )

    with col6:
        st.metric(
            "Asistencia consistente",
            f"{datos['mascaras']['asistencia_coherente'].mean() * 100:.1f}%"
        )

    st.divider()

    mostrar_interpretacion_calidad(datos)

    st.divider()

    mostrar_detalle_validaciones(df, datos)