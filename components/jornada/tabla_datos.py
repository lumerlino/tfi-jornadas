import streamlit as st


def mostrar_datos(df):

    st.subheader(
        "Datos procesados"
    )

    st.write(
        f"Registros mostrados: {len(df)}"
    )


    # Creamos una copia únicamente
    # para mostrar los datos de forma amigable.
    df_mostrar = df.copy()


    df_mostrar["fecha"] = (
        df_mostrar["fecha"]
        .dt.strftime("%d/%m/%Y")
    )


    df_mostrar[
        "hora_inicio_actividad"
    ] = (
        df_mostrar[
            "hora_inicio_actividad"
        ]
        .dt.strftime("%H:%M")
    )


    df_mostrar[
        "hora_fin_actividad"
    ] = (
        df_mostrar[
            "hora_fin_actividad"
        ]
        .dt.strftime("%H:%M")
    )


    df_mostrar[
        "hora_ingreso"
    ] = (
        df_mostrar[
            "hora_ingreso"
        ]
        .dt.strftime("%H:%M")
    )


    df_mostrar[
        "hora_egreso"
    ] = (
        df_mostrar[
            "hora_egreso"
        ]
        .dt.strftime("%H:%M")
    )


    st.dataframe(
        df_mostrar,
        use_container_width=True
    )