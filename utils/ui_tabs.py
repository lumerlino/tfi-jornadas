import streamlit as st


def mostrar_tabs(opciones, key):

    # Reemplaza st.tabs(): ese componente nativo puede "olvidar"
    # cuál pestaña estaba activa cuando el rerun lo dispara un
    # widget que vive adentro de una pestaña que no es la primera
    # (limitación conocida de Streamlit — se nota más cuanto más
    # rápido responde la app, por eso se hizo visible recién
    # después de agregar el cache). Un radio horizontal atado a
    # session_state sí mantiene la selección entre reruns, sin
    # importar qué widget los dispare.

    if key not in st.session_state:
        st.session_state[key] = opciones[0]

    st.markdown(
        """
        <style>
        div[role="radiogroup"] {
            gap: 0.25rem;
            border-bottom: 1px solid rgba(128, 128, 128, 0.3);
            padding-bottom: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    return st.radio(
        key,
        opciones,
        key=key,
        horizontal=True,
        label_visibility="collapsed"
    )
