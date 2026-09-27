import streamlit as st

from components.ui import mostrar_error

from utils.gestion_cargas import (
    listar_cargas,
    eliminar_carga,
    obtener_participaciones_carga,
    actualizar_participacion
)
from utils.historico_datos import cargar_historico
from utils.jornada_guardada import reconstruir_jornada


def mostrar_gestion_cargas():

    st.title("Jornadas guardadas")

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

            st.divider()


            # --------------------------------------------------
            # EDITAR PARTICIPACIONES
            # --------------------------------------------------

            st.markdown("#### ✏️ Editar participaciones")

            clave_cargado = f"editar_cargado_{carga['carga_id']}"

            if st.button(
                "Cargar participaciones para editar",
                key=f"btn_cargar_edicion_{carga['carga_id']}"
            ):
                st.session_state[clave_cargado] = True

            if st.session_state.get(clave_cargado):

                try:

                    df_participaciones = obtener_participaciones_carga(
                        carga["carga_id"]
                    )

                except Exception as error:

                    df_participaciones = None

                    st.warning(
                        "No se pudieron cargar las participaciones "
                        "para editar."
                    )

                    with st.expander("Detalle técnico"):
                        st.write(f"{type(error).__name__}: {error}")

                if df_participaciones is not None:

                    if df_participaciones.empty:

                        st.info(
                            "No hay participaciones para editar en "
                            "esta carga."
                        )

                    else:

                        df_editado = st.data_editor(
                            df_participaciones,
                            disabled=["id"],
                            hide_index=True,
                            use_container_width=True,
                            key=f"editor_participaciones_{carga['carga_id']}"
                        )

                        if st.button(
                            "💾 Guardar cambios en participaciones",
                            key=f"guardar_edicion_{carga['carga_id']}"
                        ):

                            filas_cambiadas = 0

                            for indice in df_participaciones.index:

                                fila_original = (
                                    df_participaciones.loc[indice]
                                )

                                fila_editada = (
                                    df_editado.loc[indice]
                                )

                                if not fila_original.equals(fila_editada):

                                    actualizar_participacion(
                                        fila_original["id"],
                                        fila_editada
                                        .drop("id")
                                        .to_dict()
                                    )

                                    filas_cambiadas += 1

                            cargar_historico.clear()
                            reconstruir_jornada.clear()

                            st.success(
                                f"Se guardaron cambios en "
                                f"{filas_cambiadas} fila(s)."
                            )

                            st.session_state[clave_cargado] = False

                            st.rerun()


            st.divider()


            # --------------------------------------------------
            # ELIMINAR CARGA
            # --------------------------------------------------

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

                try:

                    eliminar_carga(carga["carga_id"])

                except Exception as error:

                    mostrar_error(error, "No se pudo eliminar la carga")

                else:

                    cargar_historico.clear()
                    listar_cargas.clear()
                    reconstruir_jornada.clear()

                    st.success(
                        f"Carga N.º {carga['numero_carga']} de la "
                        f"jornada {carga['anio']} eliminada."
                    )
                    st.rerun()
