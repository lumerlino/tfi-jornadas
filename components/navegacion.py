import streamlit as st


# --------------------------------------------------
# Registro de páginas para navegar desde adentro de una vista.
#
# app.py crea las st.Page y las registra acá; las vistas solo
# importan este módulo (no app.py), así no hay imports circulares.
# --------------------------------------------------

PAGINAS = {}


def ir_a(clave, texto, principal=False):

    if st.button(
        texto,
        key=f"ir_a_{clave}",
        type="primary" if principal else "secondary"
    ):
        st.switch_page(PAGINAS[clave])
