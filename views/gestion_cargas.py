import streamlit as st

from utils.gestion_cargas import listar_cargas, eliminar_carga


def mostrar_gestion_cargas():

    st.title("Gestionar cargas")

    st.write(
        "Acá se pueden ver y borrar las cargas guardadas en el "
        "histórico — por ejemplo, si se subió un Excel equivocado. "
        "Borrar una carga borra también toda la asistencia asociada "
        "a ella; el Excel original no se toca, así que se puede "
        "volver a subir después si hace falta."
    )

    try:

        cargas = listar_cargas()

    except Exception as error:

        st.error(
            "No se pudo conectar con la base de datos para leer "
            "las cargas guardadas."
        )

        with st.expander("Detalle técnico"):
            st.write(f"{type(error).__name__}: {error}")

        return

    if not cargas:

        st.info(
            "Todavía no hay ninguna carga guardada en el histórico."
        )

        return


    for carga in cargas:

        titulo = (
            f"Jornada {carga['anio']} — carga N.º "
            f"{carga['numero_carga']} "
            f"({carga['cantidad_participaciones']} personas)"
        )

        with st.expander(titulo):

            st.write(f"**Año:** {carga['anio']}")
            st.write(f"**Número de carga:** {carga['numero_carga']}")
            st.write(f"**Fecha de carga:** {carga['fecha_carga']}")
            st.write(
                f"**Personas guardadas:** "
                f"{carga['cantidad_participaciones']}"
            )

            st.warning(
                "Borrar esta carga es definitivo: se eliminan todas "
                "las participaciones y la asistencia por día "
                "asociadas. Si te equivocás, hay que volver a subir "
                "el Excel original."
            )

            confirmar = st.checkbox(
                "Confirmar eliminación de esta carga",
                key=f"confirmar_borrado_{carga['carga_id']}"
            )

            if st.button(
                "🗑️ Eliminar esta carga",
                key=f"eliminar_carga_{carga['carga_id']}",
                disabled=not confirmar,
                type="primary"
            ):

                eliminar_carga(carga["carga_id"])

                st.success(
                    f"Carga N.º {carga['numero_carga']} de la "
                    f"jornada {carga['anio']} eliminada."
                )
                st.rerun()
