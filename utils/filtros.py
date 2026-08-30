import streamlit as st
import pandas as pd

from utils.limpieza_datos import (
    detectar_columnas_asistencia,
    construir_asistencia_larga
)


def aplicar_filtros(df, configuraciones=None):

    if configuraciones is None:
        configuraciones = {}

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


    # --------------------------------------------------
    # FILTROS DINÁMICOS (columnas nuevas configuradas por
    # el usuario, ver utils/configuracion_columnas.py)
    # --------------------------------------------------

    filtros_dinamicos = {}

    for columna, configuracion in configuraciones.items():

        if columna not in df.columns:
            continue

        if configuracion["tipo_dato"] not in ("categorica", "booleana"):
            continue

        valor_elegido = st.sidebar.selectbox(
            configuracion["nombre_display"],
            ["Todos"] + sorted(
                df[columna].dropna().unique().tolist(),
                key=str
            )
        )

        filtros_dinamicos[columna] = valor_elegido


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

    for columna, valor_elegido in filtros_dinamicos.items():

        if valor_elegido != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado[columna] == valor_elegido
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
