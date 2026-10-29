import pandas as pd
import streamlit as st

from utils.metricas import (
    ayuda,
    fuente_asistencia,
)
from utils.resumen_jornadas import (
    de_cada_10,
    formatear_numero,
)


def mostrar_resumen_carga(
    df,
    df_original,
    columnas_dias
):
    personas = df.dropna(
        subset=["documento"]
    )

    inscriptos = (
        personas["documento"]
        .nunique()
    )

    vinieron = (
        personas[
            personas["asistio"].astype(bool)
        ]["documento"]
        .nunique()
    )

    fuente = fuente_asistencia(
        df_original
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Se anotaron",
            formatear_numero(inscriptos),
            border=True,
            help=ayuda("se_anotaron")
        )

    with col2:
        st.metric(
            "Vinieron",
            formatear_numero(vinieron),
            border=True,
            help=ayuda(
                "vinieron",
                fuente
            )
        )

    with col3:
        st.metric(
            "De cada 10 inscriptos",
            f"{de_cada_10(vinieron, inscriptos)} vinieron",
            border=True,
            help=ayuda("de_cada_10")
        )

    with st.expander(
        "¿Cómo se calcularon estos indicadores?"
    ):

        st.write(
            f"**Se anotaron:** {formatear_numero(inscriptos)} personas únicas "
            "identificadas por número de documento."
        )

        st.write(
            f"**Vinieron:** {formatear_numero(vinieron)} personas con asistencia "
            "registrada en al menos un día."
        )

        st.write(
            f"**De cada 10 inscriptos:** "
            f"{de_cada_10(vinieron, inscriptos)} asistieron."
        )

        reinscripciones = len(df) - inscriptos

        if reinscripciones > 0:
            st.caption(
                f"{formatear_numero(reinscripciones)} registros corresponden "
                "a personas que se inscribieron más de una vez."
            )

        if columnas_dias:
            dias_sin_asistencia = []

            for columna in columnas_dias:

                tiene_asistencia = (
                    df_original[columna]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .eq("si")
                    .any()
                )

                if not tiene_asistencia:
                    dias_sin_asistencia.append(
                        columna.replace("Asistencia ", "")
                    )

            if dias_sin_asistencia:
                fechas_formateadas = (
                    pd.to_datetime(dias_sin_asistencia)
                    .strftime("%d/%m/%Y")
                    .tolist()
                )

                st.warning(
                    "No se registraron asistencias el "
                    + " y ".join(fechas_formateadas)
                    + "."
                )