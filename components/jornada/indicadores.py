import streamlit as st

from utils.calidad_datos import obtener_mascaras_calidad


def mostrar_indicadores(df):

    mascaras = obtener_mascaras_calidad(df)

    df_personas = df[
        mascaras["persona_unica"]
    ]

    df_permanencia = df[
        mascaras["permanencia"]
    ]

    df_qr = df[
        mascaras["qr"]
    ]


    # ----------------------------------------------
    # PARTICIPANTES ÚNICOS
    # ----------------------------------------------

    total_personas = (
        df_personas["id_participante"]
        .nunique()
    )


    # ----------------------------------------------
    # PARTICIPACIONES
    # ----------------------------------------------

    total_participaciones = len(df)


    # ----------------------------------------------
    # PERMANENCIA
    # ----------------------------------------------

    permanencia_promedio = (
        df_permanencia[
            "permanencia_minutos"
        ]
        .mean()
    )

    horas_promedio = int(
        permanencia_promedio // 60
    )

    minutos_promedio = int(
        permanencia_promedio % 60
    )


    # ----------------------------------------------
    # QR
    # ----------------------------------------------

    errores_qr = len(
        df_qr[
            df_qr["estado_qr"] == "Error"
        ]
    )

    total_registros_qr = len(df_qr)

    tasa_error_qr = (
        errores_qr
        / total_registros_qr
    ) * 100


    # ----------------------------------------------
    # INDICADORES
    # ----------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Participantes únicos",
            total_personas
        )

    with col2:
        st.metric(
            "Participaciones",
            total_participaciones
        )

    with col3:
        st.metric(
            "Permanencia promedio",
            f"{horas_promedio} h {minutos_promedio} min"
        )

    with col4:
        st.metric(
            "Tasa de error QR",
            f"{tasa_error_qr:.1f}%"
        )