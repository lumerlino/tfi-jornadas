import streamlit as st

from utils.guardado_historico import COLUMNAS_PARTICIPACIONES
from utils.clasificacion_columnas import (
    clasificar_columna,
    columnas_no_mapeadas,
    METRICAS_POR_TIPO,
)
from utils.configuracion_columnas import (
    obtener_configuraciones,
    guardar_configuracion,
    CONFIGURACION_POR_DEFECTO,
)
from components.ui import mostrar_error


def mostrar_columnas_nuevas(df):

    try:
        configuraciones = obtener_configuraciones()

    except Exception:
        configuraciones = CONFIGURACION_POR_DEFECTO

        st.warning(
            "No se pudo conectar con la base de configuración de "
            "columnas. Se están usando los filtros por default. "
            "Si personalizaste algo en «Columnas del formulario», "
            "esos cambios no se van a reflejar hasta que vuelva la conexión. "
            "Tampoco van a aparecer columnas nuevas para configurar por ahora."
        )

    columnas_nuevas = columnas_no_mapeadas(
        df,
        COLUMNAS_PARTICIPACIONES.keys()
    )

    pendientes = [
        columna
        for columna in columnas_nuevas
        if columna not in configuraciones
    ]

    if pendientes:

        with st.container(key="seccion_columnas"):

            st.markdown(
                "### 🆕 Columnas nuevas detectadas"
            )

            st.write(
                "Estas columnas del Excel no están contempladas todavía. "
                "No se pierden y quedan guardadas igualmente, pero para que "
                "puedan utilizarse como filtro o gráfico es necesario configurarlas."
            )

            for columna in pendientes:

                tipo = clasificar_columna(
                    df[columna]
                )

                with st.expander(
                    f"{columna} (tipo detectado: {tipo})"
                ):

                    if tipo in (
                        "identificador",
                        "texto_libre"
                    ):

                        st.info(
                            "Esta columna no se ofrece como filtro ni gráfico "
                            "porque tiene muchos valores distintos. "
                            "Puede tratarse de un identificador o de texto libre "
                            "y, por privacidad, no se expone en la aplicación."
                        )

                    else:

                        nombre_display = st.text_input(
                            "Nombre a mostrar",
                            value=columna,
                            key=f"nombre_{columna}"
                        )

                        metrica = st.selectbox(
                            "¿Qué querés ver de esta columna?",
                            METRICAS_POR_TIPO[tipo],
                            key=f"metrica_{columna}"
                        )

                        if st.button(
                            "Guardar configuración",
                            key=f"guardar_config_{columna}"
                        ):

                            try:
                                guardar_configuracion(
                                    columna,
                                    nombre_display,
                                    tipo,
                                    metrica
                                )

                            except Exception as error:
                                mostrar_error(
                                    error,
                                    "No se pudo guardar la configuración"
                                )

                            else:
                                obtener_configuraciones.clear()
                                st.rerun()
    else:
        st.success(
            "No se detectaron columnas nuevas que necesiten configuración."
        )

    return configuraciones, pendientes