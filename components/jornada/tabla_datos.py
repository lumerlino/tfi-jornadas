import streamlit as st


def mostrar_datos(df):

    st.subheader(
        "Datos procesados"
    )

    st.write(
        f"Registros mostrados: {len(df)}"
    )

    st.dataframe(
        df,
        use_container_width=True
    )
