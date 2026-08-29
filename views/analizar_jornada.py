import streamlit as st

from utils.carga_datos import cargar_datos_demo, cargar_excel_usuario
from utils.transformaciones import preparar_datos
from utils.filtros import aplicar_filtros
from utils.validaciones import validar_columnas
from utils.guardado_historico import validar_metadatos_jornada
from utils.historico_local import guardar_edicion
from components.jornada.indicadores import mostrar_indicadores
from components.jornada.participacion import mostrar_participacion
from components.jornada.permanencia import mostrar_permanencia
from components.jornada.registro_qr import mostrar_registro_qr
from components.jornada.tabla_datos import mostrar_datos
from components.jornada.ocupacion import mostrar_ocupacion
from components.jornada.calidad_datos import mostrar_calidad_datos
from components.jornada.metadatos import mostrar_metadatos_jornada


def mostrar_analizar_jornada():

    st.title("Analizar jornada")

    st.write(
        "Podés cargar un archivo Excel con los datos de una jornada "
        "o utilizar los datos de demostración."
    )


    # --------------------------------------------------
    # ESTADO DEL ANÁLISIS
    # --------------------------------------------------

    if "analisis_confirmado" not in st.session_state:
        st.session_state["analisis_confirmado"] = False

    if "editar_metadatos" not in st.session_state:
        st.session_state["editar_metadatos"] = False

    if "metadatos_jornada" not in st.session_state:
        st.session_state["metadatos_jornada"] = None


    # --------------------------------------------------
    # SELECCIÓN DEL ORIGEN DE DATOS
    # --------------------------------------------------

    opcion = st.radio(
        "¿Cómo querés comenzar?",
        [
            "📤 Cargar archivo Excel",
            "🧪 Usar datos de demostración"
        ],
        horizontal=True
    )


    df = None
    metadatos = None


    # --------------------------------------------------
    # CARGA DE ARCHIVO EXCEL
    # --------------------------------------------------

    if opcion == "📤 Cargar archivo Excel":

        archivo = st.file_uploader(
            "Seleccionar archivo Excel",
            type=["xlsx"]
        )

        if archivo is not None:

            df = cargar_excel_usuario(
                archivo
            )

            # Mostramos el formulario solamente
            # antes de confirmar el análisis
            if not st.session_state["analisis_confirmado"]:

                metadatos = mostrar_metadatos_jornada()


    # --------------------------------------------------
    # DATOS DE DEMOSTRACIÓN
    # --------------------------------------------------

    elif opcion == "🧪 Usar datos de demostración":

        st.info(
            "Se están utilizando datos ficticios generados "
            "para el desarrollo del prototipo."
        )

        df = cargar_datos_demo()


    # --------------------------------------------------
    # SI NO HAY DATOS, NO CONTINUAMOS
    # --------------------------------------------------

    if df is None:

        st.info(
            "Cargá un archivo Excel para comenzar el análisis."
        )

        return


    # --------------------------------------------------
    # VALIDACIÓN DEL ARCHIVO
    # --------------------------------------------------

    columnas_faltantes = validar_columnas(
        df
    )


    if columnas_faltantes:

        st.error(
            "El archivo no tiene el formato esperado."
        )

        st.write(
            "Faltan las siguientes columnas:"
        )

        for columna in columnas_faltantes:
            st.write(
                f"- {columna}"
            )

        return


    # --------------------------------------------------
    # BOTÓN PARA CONFIRMAR EL ANÁLISIS
    # --------------------------------------------------

    if not st.session_state["analisis_confirmado"]:

        if opcion == "📤 Cargar archivo Excel":

            if st.session_state["editar_metadatos"]:
                texto_boton = "Guardar cambios"
            else:
                texto_boton = "Analizar jornada"


            if st.button(
                texto_boton,
                type="primary"
            ):

                errores_metadatos = (
                    validar_metadatos_jornada(
                        metadatos
                    )
                )

                if errores_metadatos:

                    st.error(
                        "No se puede continuar."
                    )

                    for error in errores_metadatos:

                        st.write(
                            f"- {error}"
                        )

                else:

                    st.session_state[
                        "metadatos_jornada"
                    ] = metadatos

                    st.session_state[
                        "analisis_confirmado"
                    ] = True

                    st.session_state[
                        "editar_metadatos"
                    ] = False

                    st.rerun()


        else:

            if st.button(
                "Analizar datos de demostración",
                type="primary"
            ):

                st.session_state[
                    "analisis_confirmado"
                ] = True

                st.rerun()


        return


    # --------------------------------------------------
    # PREPARACIÓN Y LIMPIEZA DE LOS DATOS
    # --------------------------------------------------

    df, reporte_limpieza_antes, reporte_limpieza_despues = (
        preparar_datos(
            df
        )
    )

    with st.expander(
        "🧹 Ver reporte de limpieza de datos"
    ):

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("**Antes de la limpieza**")

            st.write(
                f"Filas: {reporte_limpieza_antes['filas']}"
            )

            st.write(
                f"Duplicados: {reporte_limpieza_antes['duplicados']}"
            )

            if len(reporte_limpieza_antes["nulos_por_columna"]) > 0:

                st.dataframe(
                    reporte_limpieza_antes["nulos_por_columna"]
                    .rename("Valores faltantes"),
                    use_container_width=True
                )

            else:

                st.write("Sin valores faltantes.")

        with col2:

            st.markdown("**Después de la limpieza**")

            st.write(
                f"Filas: {reporte_limpieza_despues['filas']}"
            )

            st.write(
                f"Duplicados: {reporte_limpieza_despues['duplicados']}"
            )

            if len(reporte_limpieza_despues["nulos_por_columna"]) > 0:

                st.dataframe(
                    reporte_limpieza_despues["nulos_por_columna"]
                    .rename("Valores faltantes"),
                    use_container_width=True
                )

            else:

                st.write("Sin valores faltantes.")

        st.caption(
            f"Columnas de asistencia detectadas: "
            f"{', '.join(reporte_limpieza_despues['columnas_asistencia'])}. "
            f"Inconsistencias entre 'isPresent' y la asistencia por día: "
            f"{reporte_limpieza_despues['inconsistencias_asistencia']}."
        )


    # --------------------------------------------------
    # RESUMEN DE LOS DATOS GENERALES
    # --------------------------------------------------

    if (
        opcion == "📤 Cargar archivo Excel"
        and st.session_state["metadatos_jornada"] is not None
    ):

        metadatos_guardados = (
            st.session_state[
                "metadatos_jornada"
            ]
        )

        st.markdown(
            f"### Jornada {metadatos_guardados['anio']}"
        )

        st.caption(
            f"{metadatos_guardados['fecha_inicio'].strftime('%d/%m/%Y')} "
            f"al "
            f"{metadatos_guardados['fecha_fin'].strftime('%d/%m/%Y')}"
        )


        col1, col2 = st.columns(
            [1, 1]
        )


        # --------------------------------------------------
        # EDITAR METADATA
        # --------------------------------------------------

        with col1:

            if st.button(
                "✏️ Editar datos generales",
                use_container_width=True
            ):

                st.session_state[
                    "editar_metadatos"
                ] = True

                st.session_state[
                    "analisis_confirmado"
                ] = False

                st.rerun()


        # --------------------------------------------------
        # GUARDAR EN HISTÓRICO
        # --------------------------------------------------

        with col2:

            if st.button(
                "💾 Guardar datos de la jornada",
                type="primary",
                use_container_width=True
            ):

                ruta_guardada = guardar_edicion(
                    df,
                    metadatos_guardados["anio"],
                    metadatos_guardados["fecha_inicio"],
                    metadatos_guardados["fecha_fin"],
                    es_demo=False
                )

                st.success(
                    "Los datos se guardaron correctamente en el histórico."
                )

                st.caption(
                    f"Archivo: {ruta_guardada}"
                )

    st.divider()


    # --------------------------------------------------
    # CONFIRMACIÓN DEL PROCESAMIENTO
    # --------------------------------------------------

    st.success(
        f"Jornada procesada correctamente. "
        f"Se encontraron {len(df)} registros."
    )


    # --------------------------------------------------
    # FILTROS
    # --------------------------------------------------

    df_filtrado = aplicar_filtros(
        df
    )


    # --------------------------------------------------
    # INDICADORES
    # --------------------------------------------------

    mostrar_indicadores(
        df_filtrado
    )


    st.divider()


    # --------------------------------------------------
    # PESTAÑAS DEL DASHBOARD
    # --------------------------------------------------

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "👥 Participación",
            "⏱ Permanencia",
            "🏫 Ocupación",
            "📱 Registro QR",
            "🔎 Calidad de datos",
            "📋 Datos"
        ]
    )


    with tab1:

        mostrar_participacion(
            df_filtrado
        )


    with tab2:

        mostrar_permanencia(
            df_filtrado
        )


    with tab3:

        mostrar_ocupacion(
            df_filtrado
        )


    with tab4:

        mostrar_registro_qr(
            df_filtrado
        )


    with tab5:

        mostrar_calidad_datos(
            df
        )


    with tab6:

        mostrar_datos(
            df_filtrado
        )