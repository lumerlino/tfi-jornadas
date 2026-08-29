import streamlit as st
import pandas as pd

from utils.limpieza_datos import (
    detectar_columnas_asistencia,
    construir_asistencia_larga
)


def aplicar_filtros(df):

    st.sidebar.subheader("Filtros")

    rol = st.sidebar.selectbox(
        "Rol principal",
        ["Todos"] + sorted(
            df["Rol principal"].dropna().unique().tolist()
        )
    )

    miembro_unla = st.sidebar.selectbox(
        "Miembro UNLa",
        ["Todos"] + sorted(
            df["Miembro UNLa"].dropna().unique().tolist()
        )
    )

    tipo_inscripcion = st.sidebar.selectbox(
        "Tipo de inscripción",
        ["Todos"] + sorted(
            df["Tipo inscripción"].dropna().unique().tolist()
        )
    )

    source = st.sidebar.selectbox(
        "Origen de inscripción",
        ["Todos"] + sorted(
            df["Source"].dropna().unique().tolist()
        )
    )

    columnas_asistencia = detectar_columnas_asistencia(df)

    fechas_disponibles = sorted(
        columna.replace("Asistencia ", "")
        for columna in columnas_asistencia
    )

    fecha = st.sidebar.selectbox(
        "Asistió el día",
        ["Cualquiera"] + fechas_disponibles
    )


    df_filtrado = df.copy()

    if rol != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["Rol principal"] == rol
        ]

    if miembro_unla != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["Miembro UNLa"] == miembro_unla
        ]

    if tipo_inscripcion != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["Tipo inscripción"] == tipo_inscripcion
        ]

    if source != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["Source"] == source
        ]

    if fecha != "Cualquiera":

        asistencia_larga = construir_asistencia_larga(
            df_filtrado,
            columnas_asistencia
        )

        documentos_presentes = (
            asistencia_larga[
                (asistencia_larga["fecha"] == pd.to_datetime(fecha))
                & (asistencia_larga["asistio"])
            ]
            ["documento"]
            .unique()
        )

        df_filtrado = df_filtrado[
            df_filtrado["documento"].isin(documentos_presentes)
        ]

    if len(df_filtrado) == 0:
        st.warning(
            "No hay datos que coincidan "
            "con los filtros seleccionados."
        )
        st.stop()

    return df_filtrado
