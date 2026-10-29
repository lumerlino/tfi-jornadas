import io
import streamlit as st

from utils.carga_datos import cargar_excel_usuario
from utils.validaciones import validar_columnas
from utils.guardado_historico import (
    validar_metadatos_jornada,
    guardar_carga
)

from utils.historico_datos import cargar_historico
from utils.gestion_cargas import listar_cargas
from utils.jornada_guardada import reconstruir_jornada
from components.jornada.metadatos import mostrar_metadatos_jornada
from views.dashboard_jornada import mostrar_dashboard_jornada
from components.navegacion import ir_a
from components.jornada.limpieza_jornada import (
    preparar_y_mostrar_limpieza,
)
from components.jornada.columnas_nuevas import (
    mostrar_columnas_nuevas,
)
from components.jornada.resumen_carga import (
    mostrar_resumen_carga,
)
from components.jornada.cambios_formulario import (
    mostrar_cambios_formulario,
)
from components.ui import (
    PASOS_CARGA,
    mostrar_archivo_cargado,
    mostrar_error,
    mostrar_pasos,
)

# El tablero completo del archivo (el dashboard anterior) queda
# oculto: abrumaba al terminar la carga. El código sigue; para
# volver a ofrecerlo alcanza con poner esto en True.
MOSTRAR_TABLERO_COMPLETO = False


def _cambiar_archivo():

    # Vuelve al paso 1: descarta el archivo y todo lo que dependía
    # de él. El contador renueva la key del file_uploader para que
    # aparezca vacío.
    for clave in ("archivo_excel", "carga_guardada", "animar_pasos_desde"):
        st.session_state.pop(clave, None)

    st.session_state["analisis_confirmado"] = False
    st.session_state["editar_metadatos"] = False
    st.session_state["metadatos_jornada"] = None
    st.session_state["subidas_excel"] = st.session_state.get("subidas_excel", 0) + 1


def mostrar_analizar_jornada():

    st.title("Nueva jornada")

    # La introducción explica el recorrido completo y solo se muestra
    # mientras no hay un Excel cargado: después, la guía de pasos ya
    # dice qué sigue.
    if st.session_state.get("archivo_excel") is None:

        st.write(
            "Subí el Excel de inscripción y asistencia de la jornada "
            "para revisarlo, limpiarlo y guardarlo en el histórico."
        )

    # La guía existe durante todo el flujo.
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

    opcion = "📤 Cargar archivo Excel"

    df = None
    metadatos = None


    # --------------------------------------------------
    # CARGA DE ARCHIVO EXCEL
    # --------------------------------------------------

    if opcion == "📤 Cargar archivo Excel":

        # El Excel subido se guarda en session_state y el
        # file_uploader deja de mostrarse: en su lugar queda una
        # sola línea con el archivo y "Cambiar archivo".
        archivo_guardado = st.session_state.get("archivo_excel")

        if archivo_guardado is None:

            with st.container(key="seccion_subir"):

                archivo = st.file_uploader(
                    "Excel de inscripción y asistencia de la jornada",
                    type=["xlsx"],
                    key=f"subir_excel_{st.session_state.get('subidas_excel', 0)}"
                )

                if archivo is not None:

                    st.session_state["archivo_excel"] = {
                        "nombre": archivo.name,
                        "datos": archivo.getvalue()
                    }

                    st.rerun()

        else:

            df = cargar_excel_usuario(
                io.BytesIO(archivo_guardado["datos"])
            )

            mostrar_archivo_cargado(
                archivo_guardado["nombre"],
                len(df),
                al_cambiar=_cambiar_archivo,
                key="cambiar_archivo_excel"
            )

            # Mostramos el formulario solamente
            # antes de confirmar el análisis
            if not st.session_state["analisis_confirmado"]:

                seccion_analizar = st.container(key="seccion_analizar")

                with seccion_analizar:
                    metadatos = mostrar_metadatos_jornada(df)


    # --------------------------------------------------
    # SI NO HAY DATOS, NO CONTINUAMOS
    # --------------------------------------------------

    carga_excel = opcion == "📤 Cargar archivo Excel"

    if df is None:

        # Sin aviso extra: la frase de arriba y el paso 1 resaltado
        # ya dicen qué hacer.
        if carga_excel:
            mostrar_pasos(guia_pasos, 0)

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

            with seccion_analizar:

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

        return


    # --------------------------------------------------
    # PREPARACIÓN Y LIMPIEZA DE LOS DATOS
    # --------------------------------------------------

    (
        df_original,
        df,
        reporte_limpieza_antes,
        reporte_limpieza_despues,
    ) = preparar_y_mostrar_limpieza(df)


    # --------------------------------------------------
    # COLUMNAS NUEVAS: detectar, clasificar y preguntar
    # --------------------------------------------------

    configuraciones, pendientes = mostrar_columnas_nuevas(df)

    # Limpiar es automático:
    # si hay columnas nuevas, estamos en el paso 4;
    # si no, ya corresponde guardar.

    mostrar_pasos(
        guia_pasos,
        3 if pendientes else 4,
        animar_desde=st.session_state.pop(
            "animar_pasos_desde",
            None
        )
    )


    with st.container(key="seccion_guardar"):

        mostrar_cambios_formulario(df, st.session_state.get("metadatos_jornada"))

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

        mostrar_resumen_carga(
            df,
            df_original,
            reporte_limpieza_despues["columnas_asistencia"]
        )

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
                    use_container_width=True,
                    disabled="carga_guardada" in st.session_state
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

                        st.session_state["carga_guardada"] = {
                            "anio": metadatos_guardados["anio"],
                            "numero_carga": resultado_carga["numero_carga"]
                        }

                        st.session_state["animar_pasos_desde"] = 4

                        st.rerun()

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
