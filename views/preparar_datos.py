import streamlit as st

from components.navegacion import ir_a, tarjeta
from components.ui import PASOS_CARGA


# --------------------------------------------------
# "PREPARAR DATOS": la trastienda de la app.
#
# Una sola entrada en el menú; desde acá se llega a cada tarea.
# Tono orientado a tareas, distinto del de las tres preguntas.
# --------------------------------------------------


def mostrar_preparar_datos():

    st.title("Preparar datos")

    st.write(
        "Cargar una jornada nueva, revisar las que ya están guardadas y "
        "ajustar cómo se leen las columnas del formulario de inscripción."
    )

    # --------------------------------------------------
    # CARGAR JORNADA NUEVA: la tarea principal, a lo ancho
    # --------------------------------------------------

    with tarjeta("nueva_jornada"):

        st.subheader("Nueva jornada")

        st.caption(
            "Se sube el Excel de inscripción y asistencia de una edición; "
            "la app lo revisa y lo limpia antes de guardarlo."
        )

        columnas_pasos = st.columns(len(PASOS_CARGA))

        for numero, (columna, paso) in enumerate(zip(columnas_pasos, PASOS_CARGA), start=1):

            with columna:
                st.markdown(f":gray[Paso {numero}]  \n**{paso}**")

        ir_a("cargar_jornada", "Empezar", principal=True)

    # --------------------------------------------------
    # EL RESTO DE LAS TAREAS
    # --------------------------------------------------

    tareas = [
        (
            "Jornadas guardadas",
            "Ver las cargas de cada edición y borrar las que estén "
            "repetidas o equivocadas.",
            "jornadas_guardadas",
            "Abrir",
        ),
        (
            "Columnas del formulario",
            "Qué hace la app con cada columna del Excel, incluidas las "
            "que se agregaron al formulario en ediciones nuevas.",
            "columnas",
            "Abrir",
        ),
    ]

    for columna, (titulo, descripcion, clave, boton) in zip(st.columns(len(tareas)), tareas):

        with columna:

            with tarjeta(clave, height="stretch"):

                st.markdown(f"#### {titulo}")
                st.caption(descripcion)
                ir_a(clave, boton)
