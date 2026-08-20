import streamlit as st


def mostrar_inicio():

    st.title(
        "Jornadas de Investigación"
    )

    st.write(
        "Plataforma para el análisis de datos "
        "de las Jornadas de Investigación."
    )

    st.divider()

    col1, col2 = st.columns(2)


    with col1:

        st.markdown(
            "## 📤 Analizar una jornada"
        )

        st.write(
            "Cargá los datos de una jornada y obtené "
            "indicadores, gráficos y estadísticas."
        )

        if st.button(
            "Analizar jornada",
            use_container_width=True
        ):

            st.session_state["pagina"] = (
                "📤 Analizar jornada"
            )

            st.rerun()


    with col2:

        st.markdown(
            "## 📊 Consultar histórico"
        )

        st.write(
            "Compará los resultados de distintas "
            "ediciones de las Jornadas."
        )

        if st.button(
            "Ver histórico",
            use_container_width=True
        ):

            st.session_state["pagina"] = (
                "📊 Histórico"
            )

            st.rerun()