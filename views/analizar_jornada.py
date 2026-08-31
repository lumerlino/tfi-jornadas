import os

import streamlit as st

from utils.carga_datos import cargar_datos_demo, cargar_excel_usuario
from utils.transformaciones import preparar_datos
from utils.filtros import aplicar_filtros
from utils.validaciones import validar_columnas
from utils.guardado_historico import (
    validar_metadatos_jornada,
    guardar_carga,
    COLUMNAS_PARTICIPACIONES
)
from utils.clasificacion_columnas import (
    clasificar_columna,
    columnas_no_mapeadas,
    METRICAS_POR_TIPO
)
from utils.configuracion_columnas import (
    obtener_configuraciones,
    guardar_configuracion,
    CONFIGURACION_POR_DEFECTO
)
from components.jornada.indicadores import mostrar_indicadores
from components.jornada.participacion import mostrar_participacion
from components.jornada.tabla_datos import mostrar_datos
from components.jornada.calidad_datos import mostrar_calidad_datos
from components.jornada.metadatos import mostrar_metadatos_jornada
from components.jornada.explorar import mostrar_explorar


def mostrar_analizar_jornada():

    st.title("Analizar jornada")

    demo_habilitado = (
        os.getenv("HABILITAR_DEMO", "false").lower() == "true"
    )

    if demo_habilitado:

        st.write(
            "Podés cargar un archivo Excel con los datos de una jornada "
            "o utilizar los datos de demostración."
        )

    else:

        st.write(
            "Cargá un archivo Excel con los datos de una jornada "
            "para comenzar el análisis."
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

    opciones_origen = ["📤 Cargar archivo Excel"]

    if demo_habilitado:
        opciones_origen.append("🧪 Usar datos de demostración")

    if len(opciones_origen) > 1:

        opcion = st.radio(
            "¿Cómo querés comenzar?",
            opciones_origen,
            horizontal=True
        )

    else:

        opcion = opciones_origen[0]


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

                metadatos = mostrar_metadatos_jornada(df)


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

        columnas_asistencia_detectadas = (
            reporte_limpieza_despues["columnas_asistencia"]
        )

        if columnas_asistencia_detectadas:

            st.caption(
                f"Columnas de asistencia detectadas: "
                f"{', '.join(columnas_asistencia_detectadas)}. "
                f"Inconsistencias entre 'isPresent' y la asistencia "
                f"por día: "
                f"{reporte_limpieza_despues['inconsistencias_asistencia']}."
            )

        else:

            st.caption(
                "Este archivo no trae columnas de asistencia por "
                "día ('Asistencia YYYY-MM-DD') — se usa 'isPresent' "
                "directamente como fuente de asistencia."
            )


    # --------------------------------------------------
    # COLUMNAS NUEVAS: detectar, clasificar y preguntar
    # --------------------------------------------------

    try:

        configuraciones = obtener_configuraciones()

    except Exception:

        configuraciones = CONFIGURACION_POR_DEFECTO

        st.warning(
            "No se pudo conectar con la base de configuración de "
            "columnas. Se están usando los filtros por default — si "
            "personalizaste algo en ⚙️ Configuración, esos cambios no "
            "se van a reflejar hasta que vuelva la conexión. Tampoco "
            "van a aparecer columnas nuevas para configurar por ahora."
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

        st.markdown("### 🆕 Columnas nuevas detectadas")

        st.write(
            "Estas columnas del Excel no están contempladas todavía. "
            "No se pierden (quedan guardadas igual), pero para que "
            "aparezcan como filtro o gráfico hay que configurarlas."
        )

        for columna in pendientes:

            tipo = clasificar_columna(df[columna])

            with st.expander(f"{columna} (tipo detectado: {tipo})"):

                if tipo in ("identificador", "texto_libre"):

                    st.info(
                        "Esta columna no se ofrece como filtro ni "
                        "gráfico: tiene muchos valores distintos "
                        "(puede ser un identificador o texto libre), "
                        "y por privacidad no se expone en la app."
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

                        guardar_configuracion(
                            columna,
                            nombre_display,
                            tipo,
                            metrica
                        )

                        st.rerun()


    # --------------------------------------------------
    # VISTA DE ANÁLISIS: solo columnas oficiales + asistencia
    # + configuradas. El "df" completo (con todo lo que trajo
    # el Excel) se sigue usando para guardar en Supabase más
    # abajo, así "datos_extra" no pierde nada — esto solo
    # recorta lo que se filtra/grafica/muestra en pantalla.
    # --------------------------------------------------

    columnas_a_mantener = (
        set(COLUMNAS_PARTICIPACIONES.keys())
        | set(reporte_limpieza_despues["columnas_asistencia"])
        | set(configuraciones.keys())
    )

    df_vista = df[
        [
            columna
            for columna in df.columns
            if columna in columnas_a_mantener
        ]
    ]


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

                resultado_carga = guardar_carga(
                    df=df,
                    metadatos=metadatos_guardados
                )

                st.success(
                    "Los datos se guardaron correctamente en el histórico."
                )

                st.caption(
                    f"Carga N.º {resultado_carga['numero_carga']} "
                    f"guardada para la jornada {metadatos_guardados['anio']}."
                )

    st.divider()


    # --------------------------------------------------
    # CONFIRMACIÓN DEL PROCESAMIENTO
    # --------------------------------------------------

    st.success(
        f"Jornada procesada correctamente. "
        f"Se encontraron {len(df)} registros."
    )

    st.caption(
        "ℹ️ Permanencia, Ocupación de aulas y Registro QR no están "
        "disponibles con este sistema de inscripción: el archivo no "
        "trae horarios de ingreso/egreso, asignación de aulas ni un "
        "log de lecturas QR — solo el código asignado a cada "
        "persona. Si el sistema de origen empieza a registrar esos "
        "datos, estas vistas se pueden reactivar (el código ya "
        "existe en components/jornada/)."
    )


    # --------------------------------------------------
    # FILTROS
    # --------------------------------------------------

    df_filtrado = aplicar_filtros(
        df_vista,
        configuraciones
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

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "👥 Participación",
            "🔎 Calidad de datos",
            "📋 Datos",
            "📈 Explorar"
        ]
    )


    with tab1:

        mostrar_participacion(
            df_filtrado
        )


    with tab2:

        mostrar_calidad_datos(
            df_vista
        )


    with tab3:

        mostrar_datos(
            df_filtrado
        )


    with tab4:

        mostrar_explorar(
            df_filtrado,
            configuraciones
        )