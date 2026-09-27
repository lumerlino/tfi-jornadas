import os

import streamlit as st

from utils.carga_datos import cargar_datos_demo, cargar_excel_usuario
from utils.transformaciones import preparar_datos
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
from utils.historico_datos import cargar_historico
from utils.gestion_cargas import listar_cargas
from utils.jornada_guardada import reconstruir_jornada
from components.jornada.metadatos import mostrar_metadatos_jornada
from views.dashboard_jornada import mostrar_dashboard_jornada
from components.navegacion import ir_a
from components.ui import PASOS_CARGA, mostrar_error, mostrar_pasos
from utils.resumen_jornadas import de_cada_10, formatear_numero


# El tablero completo del archivo (el dashboard anterior) queda
# oculto: abrumaba al terminar la carga. El código sigue; para
# volver a ofrecerlo alcanza con poner esto en True.
MOSTRAR_TABLERO_COMPLETO = False


def mostrar_analizar_jornada():

    st.title("Cargar jornada nueva")

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


    # Guía de pasos: se reserva el lugar arriba y se completa más
    # abajo, cuando ya se sabe en qué paso está la carga.
    guia_pasos = st.empty()


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

    carga_excel = opcion == "📤 Cargar archivo Excel"

    if df is None:

        if carga_excel:
            mostrar_pasos(guia_pasos, 0)

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

        if carga_excel:
            mostrar_pasos(guia_pasos, 1)

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

        if carga_excel:
            mostrar_pasos(guia_pasos, 1)

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

                    st.session_state.pop("carga_guardada", None)

                    # En el próximo render los pasos 2 a 4 se
                    # "encienden" en secuencia (ver mostrar_pasos).
                    st.session_state["animar_pasos_desde"] = 1

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
            "personalizaste algo en «Columnas del formulario», esos cambios no "
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

    # Limpiar (paso 3) es automático: si hay columnas nuevas, la
    # persona está en el paso 4; si no, ya le toca guardar.
    if carga_excel:
        mostrar_pasos(
            guia_pasos,
            3 if pendientes else 4,
            animar_desde=st.session_state.pop("animar_pasos_desde", None)
        )

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

                        try:

                            guardar_configuracion(
                                columna,
                                nombre_display,
                                tipo,
                                metrica
                            )

                        except Exception as error:

                            mostrar_error(error, "No se pudo guardar la configuración")

                        else:

                            obtener_configuraciones.clear()

                            st.rerun()


    # --------------------------------------------------
    # RESUMEN DE LA CARGA
    #
    # Al terminar la carga se muestra solo lo necesario para
    # confirmar que el archivo está bien y guardarlo. El análisis
    # (comparado con otros años) vive en "Cómo nos fue"; el tablero
    # completo del archivo queda plegado al final.
    # --------------------------------------------------

    st.success(
        f"Listo: el archivo se leyó y se limpió sin problemas "
        f"({formatear_numero(len(df))} registros)."
    )

    if (
        opcion == "📤 Cargar archivo Excel"
        and st.session_state["metadatos_jornada"] is not None
    ):

        metadatos_guardados = (
            st.session_state[
                "metadatos_jornada"
            ]
        )

        st.subheader(f"Jornada {metadatos_guardados['anio']}")

        st.caption(
            f"{metadatos_guardados['fecha_inicio'].strftime('%d/%m/%Y')} "
            f"al "
            f"{metadatos_guardados['fecha_fin'].strftime('%d/%m/%Y')}"
        )

    else:

        st.subheader("Resumen de los datos")

    mostrar_resumen_carga(df)

    if (
        opcion == "📤 Cargar archivo Excel"
        and st.session_state["metadatos_jornada"] is not None
    ):

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

                try:

                    resultado_carga = guardar_carga(
                        df=df,
                        metadatos=metadatos_guardados
                    )

                except Exception as error:

                    resultado_carga = None
                    error_guardado = error

                if resultado_carga is not None:

                    cargar_historico.clear()
                    listar_cargas.clear()
                    reconstruir_jornada.clear()

                    # El aviso y el botón de "Cómo nos fue" tienen que
                    # sobrevivir al rerun que dispara ese botón.
                    st.session_state["carga_guardada"] = {
                        "anio": metadatos_guardados["anio"],
                        "numero_carga": resultado_carga["numero_carga"]
                    }

                    st.session_state["animar_pasos_desde"] = 4

                else:

                    st.session_state["error_guardado"] = error_guardado

        # Fuera de las columnas, para que el aviso ocupe el ancho.
        error_guardado = st.session_state.pop("error_guardado", None)

        if error_guardado is not None:
            mostrar_error(error_guardado, "No se pudo guardar la jornada en el histórico")

        carga_guardada = st.session_state.get("carga_guardada")

        if carga_guardada:

            mostrar_pasos(
                guia_pasos,
                len(PASOS_CARGA),
                terminado=True,
                animar_desde=st.session_state.pop("animar_pasos_desde", None)
            )

            st.success(
                f"Guardada en el histórico: jornada {carga_guardada['anio']}, "
                f"carga N.º {carga_guardada['numero_carga']}."
            )

            ir_a("como_nos_fue", "Ver cómo nos fue →", principal=True)


    # --------------------------------------------------
    # TABLERO COMPLETO DEL ARCHIVO (a pedido)
    # Compartido con "Ver jornada" en Explorar en detalle,
    # ver views/dashboard_jornada.py. Va con un toggle y no con un
    # expander: el contenido de un expander se ejecuta aunque esté
    # cerrado, y el tablero dibuja sus filtros en la barra lateral.
    # --------------------------------------------------

    if MOSTRAR_TABLERO_COMPLETO and st.toggle(
        "Ver todos los gráficos de este archivo",
        key="ver_tablero_completo",
        help=(
            "Es el análisis completo de este archivo por sí solo. Para "
            "ver cómo nos fue comparado con otros años, guardá la "
            "jornada y abrí «Cómo nos fue»."
        )
    ):

        mostrar_dashboard_jornada(
            df,
            configuraciones
        )


def mostrar_resumen_carga(df):

    personas = df.dropna(subset=["documento"])

    inscriptos = personas["documento"].nunique()
    vinieron = personas[personas["asistio"].astype(bool)]["documento"].nunique()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Se anotaron", formatear_numero(inscriptos), border=True)

    with col2:
        st.metric("Vinieron", formatear_numero(vinieron), border=True)

    with col3:
        st.metric(
            "De cada 10 inscriptos",
            f"{de_cada_10(vinieron, inscriptos)} vinieron",
            border=True
        )
