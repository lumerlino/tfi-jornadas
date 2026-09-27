import streamlit as st

from components.ui import mostrar_error

from utils.clasificacion_columnas import METRICAS_POR_TIPO
from utils.configuracion_columnas import (
    obtener_configuraciones,
    guardar_configuracion,
    eliminar_configuracion,
    obtener_valores_columna
)
from components.jornada.explorar import renderizar_metrica


def mostrar_configuracion_columnas():

    st.title("Columnas del formulario")

    st.write(
        "Acá se pueden editar o eliminar las configuraciones de "
        "columnas que la app no conoce de entrada (ver la sección "
        "'Columnas nuevas detectadas' en «Cargar jornada nueva»)."
    )

    try:

        configuraciones = obtener_configuraciones()

    except Exception as error:

        st.error(
            "No se pudo conectar con la base de datos para leer las "
            "configuraciones de columnas."
        )

        with st.expander("Detalle técnico"):
            st.write(f"{type(error).__name__}: {error}")

        return

    if not configuraciones:

        st.info(
            "Todavía no hay ninguna columna configurada."
        )

        return


    for columna_excel, configuracion in configuraciones.items():

        with st.expander(columna_excel):

            st.caption(
                f"Tipo de dato detectado: {configuracion['tipo_dato']}"
            )

            nombre_display = st.text_input(
                "Nombre a mostrar",
                value=configuracion["nombre_display"],
                key=f"config_nombre_{columna_excel}"
            )

            metricas_disponibles = METRICAS_POR_TIPO.get(
                configuracion["tipo_dato"],
                [configuracion["metrica"]]
            )

            indice_actual = (
                metricas_disponibles.index(configuracion["metrica"])
                if configuracion["metrica"] in metricas_disponibles
                else 0
            )

            metrica = st.selectbox(
                "Métrica",
                metricas_disponibles,
                index=indice_actual,
                key=f"config_metrica_{columna_excel}"
            )

            st.markdown("**Vista previa**")

            try:

                valores = obtener_valores_columna(columna_excel)

                if valores.dropna().empty:

                    st.info(
                        "Todavía no hay datos guardados para esta "
                        "columna (nadie guardó una jornada que la "
                        "traiga)."
                    )

                elif metrica != "Ninguna":

                    renderizar_metrica(
                        valores,
                        nombre_display,
                        metrica,
                        key_prefix=f"config_preview_{columna_excel}"
                    )

                else:

                    st.caption("Métrica 'Ninguna': no se muestra gráfico.")

            except Exception as error:

                st.warning(
                    "No se pudo cargar la vista previa con datos reales."
                )

                with st.expander("Detalle técnico"):
                    st.write(f"{type(error).__name__}: {error}")


            col1, col2 = st.columns([1, 1])

            with col1:

                if st.button(
                    "💾 Guardar cambios",
                    key=f"config_guardar_{columna_excel}",
                    use_container_width=True
                ):

                    try:

                        guardar_configuracion(
                            columna_excel,
                            nombre_display,
                            configuracion["tipo_dato"],
                            metrica
                        )

                    except Exception as error:

                        mostrar_error(error, "No se pudo guardar la configuración")

                    else:

                        obtener_configuraciones.clear()

                        st.success("Configuración actualizada.")
                        st.rerun()

            with col2:

                confirmar = st.checkbox(
                    "Confirmar eliminación",
                    key=f"config_confirmar_{columna_excel}"
                )

                if st.button(
                    "🗑️ Eliminar configuración",
                    key=f"config_eliminar_{columna_excel}",
                    disabled=not confirmar,
                    use_container_width=True
                ):

                    try:

                        eliminar_configuracion(columna_excel)

                    except Exception as error:

                        mostrar_error(error, "No se pudo eliminar la configuración")

                    else:

                        obtener_configuraciones.clear()

                        st.success(
                            "Configuración eliminada. La columna va a "
                            "volver a aparecer como pendiente la próxima "
                            "vez que se analice una jornada que la traiga."
                        )
                        st.rerun()
