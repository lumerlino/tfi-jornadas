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


    # --------------------------------------------------
    # FILTROS POR COLUMNA (oficiales sembrados por default
    # + los que se vayan configurando dinámicamente — todos
    # viven en la misma tabla, ver utils/configuracion_columnas.py)
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


    # --------------------------------------------------
    # ASISTIÓ EL DÍA (no es una columna única, se arma
    # cruzando las columnas "Asistencia YYYY-MM-DD" — queda
    # aparte del sistema de configuración por columna)
    # --------------------------------------------------

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
