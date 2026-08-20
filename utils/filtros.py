import streamlit as st


def aplicar_filtros(df):

    st.sidebar.subheader("Filtros")

    fecha = st.sidebar.selectbox(
        "Fecha",
        ["Todas"] + sorted(
            df["fecha_texto"].unique().tolist()
        )
    )

    actividad = st.sidebar.selectbox(
        "Actividad",
        ["Todas"] + sorted(
            df["actividad"].unique().tolist()
        )
    )

    carrera = st.sidebar.selectbox(
        "Carrera",
        ["Todas"] + sorted(
            df["carrera"].unique().tolist()
        )
    )

    tipo = st.sidebar.selectbox(
        "Tipo de participante",
        ["Todos"] + sorted(
            df["tipo_participante"].unique().tolist()
        )
    )

    df_filtrado = df.copy()

    if fecha != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["fecha_texto"] == fecha
        ]

    if actividad != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["actividad"] == actividad
        ]

    if carrera != "Todas":
        df_filtrado = df_filtrado[
            df_filtrado["carrera"] == carrera
        ]

    if tipo != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["tipo_participante"] == tipo
        ]

    if len(df_filtrado) == 0:
        st.warning(
            "No hay datos que coincidan "
            "con los filtros seleccionados."
        )
        st.stop()

    return df_filtrado