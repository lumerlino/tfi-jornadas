import html
import traceback

import streamlit as st

from utils.tema import COLORES


# --------------------------------------------------
# COMPONENTES VISUALES PROPIOS
#
# Patrones que Streamlit no trae y se repiten entre pantallas.
# El color nunca va solo: cada estado lleva ícono y etiqueta.
# --------------------------------------------------

# Colores fijos (no dependen del modo): el tema que detecta el
# servidor (st.context.theme) puede llegar desfasado del que ve el
# navegador, y estos tonos se leen bien sobre fondo claro y oscuro.
ESTADOS = {
    "bajo": {"icono": "▼", "etiqueta": "Bajó", "fondo": COLORES["light"]["bajo"], "tinta": "#ffffff"},
    "subio": {"icono": "▲", "etiqueta": "Subió", "fondo": COLORES["light"]["subio"], "tinta": "#ffffff"},
    "atencion": {"icono": "!", "etiqueta": "Atención", "fondo": COLORES["light"]["atencion"], "tinta": "#0b0b0b"},
    "igual": {"icono": "=", "etiqueta": "Sin cambios", "fondo": "#9aa0a8", "tinta": "#0b0b0b"},
}


def mostrar_hallazgos(lista):

    st.markdown(
        """
        <style>
        .hallazgo {
            display: grid;
            grid-template-columns: 1.6rem minmax(0, 1fr);
            gap: 0.75rem;
            align-items: start;
            border: 1px solid rgba(128, 128, 128, 0.28);
            border-radius: 0.5rem;
            padding: 0.75rem 1rem;
            margin-bottom: 0.6rem;
        }
        .hallazgo .icono {
            width: 1.6rem;
            height: 1.6rem;
            border-radius: 50%;
            display: grid;
            place-items: center;
            font-size: 0.75rem;
            font-weight: 800;
        }
        .hallazgo .etiqueta {
            display: block;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            opacity: 0.7;
        }
        .hallazgo .texto {
            font-size: 1.02rem;
            line-height: 1.45;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    for hallazgo in lista:

        estado = ESTADOS[hallazgo["tipo"]]

        st.markdown(
            f"""
            <div class="hallazgo">
                <span class="icono" style="background:{estado["fondo"]};color:{estado["tinta"]}">{estado["icono"]}</span>
                <div>
                    <span class="etiqueta">{estado["etiqueta"]}</span>
                    <span class="texto">{html.escape(hallazgo["texto"])}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def selector_anio(anios, key):

    # Las pantallas comparten el año elegido: el widget de cada una
    # se borra al cambiar de página, así que el valor vive aparte.

    opciones = sorted(anios, reverse=True)

    guardado = st.session_state.get("anio_elegido")

    anio = st.selectbox(
        "Ver otra jornada",
        opciones,
        index=opciones.index(guardado) if guardado in opciones else 0,
        key=key
    )

    st.session_state["anio_elegido"] = anio

    return anio



# Pasos del flujo de carga (views/analizar_jornada.py). Se muestran
# en "Preparar datos" y como guía arriba de la carga.
PASOS_CARGA = [
    "Subir el Excel",
    "Analizar el archivo",
    "Limpiar los datos",
    "Revisar columnas nuevas",
    "Guardar en el histórico",
]


# Tiempo entre que se enciende un paso y el siguiente (segundos).
PAUSA_ANIMACION = 0.45


def mostrar_pasos(destino, actual, terminado=False, animar_desde=None):

    # actual: índice (desde 0) del paso en el que está la persona.
    # El paso actual va resaltado en bordó; los anteriores con ✓.
    # animar_desde: si viene, los pasos desde ese índice hasta el
    # actual se "encienden" uno tras otro (se usa justo después de
    # Analizar y de Guardar, una sola vez). Colores fijos: se leen
    # en modo claro y oscuro.

    marca = COLORES["light"]["marca"]

    ultimo = len(PASOS_CARGA) if terminado else actual

    items = []

    for indice, paso in enumerate(PASOS_CARGA):

        estilo = ""

        if terminado or indice < actual:
            clase, prefijo = "hecho", "✓"
        elif indice == actual:
            clase, prefijo = "actual", str(indice + 1)
        else:
            clase, prefijo = "pendiente", str(indice + 1)

        if animar_desde is not None and animar_desde <= indice <= ultimo:

            orden = indice - animar_desde

            if clase == "hecho":
                clase += " anim-listo"
            elif clase == "actual":
                clase += " anim-actual"

            estilo = f' style="animation-delay:{orden * PAUSA_ANIMACION:.2f}s"'

        items.append(
            f'<li class="{clase}"{estilo}><span class="num">{prefijo}</span>'
            f'<span class="nombre">{html.escape(paso)}</span></li>'
        )

    destino.markdown(
        f"""
        <style>
        .pasos-carga {{
            list-style: none;
            margin: 0 0 0.5rem 0;
            padding: 0;
            display: grid;
            grid-template-columns: repeat({len(PASOS_CARGA)}, minmax(0, 1fr));
            gap: 0.5rem;
        }}
        .pasos-carga li {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border: 1px solid rgba(128, 128, 128, 0.3);
            border-radius: 0.5rem;
            padding: 0.5rem 0.65rem;
            font-size: 0.9rem;
            line-height: 1.25;
        }}
        .pasos-carga .num {{
            flex: none;
            width: 1.4rem;
            height: 1.4rem;
            border-radius: 50%;
            display: grid;
            place-items: center;
            font-size: 0.75rem;
            font-weight: 700;
            border: 1px solid currentColor;
        }}
        /* Paso hecho: círculo bordó con ✓ blanco; el nombre atenuado
           para que no compita con el paso actual. */
        .pasos-carga li.hecho .num {{
            background: {marca};
            border-color: {marca};
            color: #ffffff;
        }}
        .pasos-carga li.hecho .nombre {{ opacity: 0.7; }}
        .pasos-carga li.pendiente {{ opacity: 0.45; }}
        .pasos-carga li.actual {{
            background: {marca};
            border-color: {marca};
            color: #ffffff;
            font-weight: 600;
        }}
        @keyframes paso-listo {{
            0%   {{ opacity: 0.45; background: transparent; color: inherit; border-color: rgba(128, 128, 128, 0.3); }}
            45%  {{ opacity: 1; background: {marca}; color: #ffffff; border-color: {marca}; }}
            100% {{ opacity: 1; background: transparent; color: inherit; border-color: rgba(128, 128, 128, 0.3); }}
        }}
        @keyframes paso-actual {{
            0%   {{ opacity: 0.45; background: transparent; color: inherit; border-color: rgba(128, 128, 128, 0.3); }}
            100% {{ opacity: 1; background: {marca}; color: #ffffff; border-color: {marca}; }}
        }}
        .pasos-carga li.anim-listo {{ animation: paso-listo 0.9s ease both; }}
        .pasos-carga li.anim-actual {{ animation: paso-actual 0.5s ease both; }}
        @media (prefers-reduced-motion: reduce) {{
            .pasos-carga li.anim-listo, .pasos-carga li.anim-actual {{ animation: none; }}
        }}
        @media (max-width: 640px) {{
            .pasos-carga {{ grid-template-columns: minmax(0, 1fr); }}
        }}
        </style>
        <ol class="pasos-carga" aria-label="Pasos de la carga">
            {"".join(items)}
        </ol>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# ERRORES AL LEER O ESCRIBIR EN LA BASE
#
# Un aviso de una línea; el tipo de error y el traceback quedan
# plegados en "Detalle técnico" para quien tenga que diagnosticar.
# --------------------------------------------------


def es_error_de_conexion(error):

    try:
        import httpx
    except ImportError:
        return False

    return isinstance(error, (httpx.TransportError, httpx.TimeoutException))


def mostrar_error(error, que_fallo):

    if es_error_de_conexion(error):
        st.error(
            f"{que_fallo}: no hay conexión con la base de datos. "
            "Probá de nuevo en unos minutos."
        )
    else:
        st.error(
            f"{que_fallo}. Si vuelve a pasar, el detalle técnico "
            "ayuda a encontrar la causa."
        )

    with st.expander("Detalle técnico"):
        st.caption(f"{type(error).__name__}: {error}")
        st.code(
            "".join(traceback.format_exception(error)),
            language=None
        )


# --------------------------------------------------
# ARCHIVO CARGADO: reemplaza al file_uploader una vez subido el
# Excel, para no repetir el archivo en dos filas. Mismo círculo
# bordó con ✓ que un paso completo de la guía de carga.
# --------------------------------------------------


def mostrar_archivo_cargado(nombre, registros, al_cambiar, key):

    marca = COLORES["light"]["marca"]

    cantidad = f"{int(registros):,}".replace(",", ".")

    with st.container(border=True):

        col_archivo, col_boton = st.columns(
            [4, 1],
            vertical_alignment="center"
        )

        with col_archivo:

            st.markdown(
                f"""
                <div style="display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap;">
                    <span style="flex:none;width:1.4rem;height:1.4rem;border-radius:50%;
                        display:grid;place-items:center;font-size:0.75rem;font-weight:700;
                        background:{marca};color:#ffffff;">✓</span>
                    <span style="font-weight:600;overflow-wrap:anywhere;">{html.escape(nombre)}</span>
                    <span style="opacity:0.7;">· {cantidad} filas</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_boton:

            st.button(
                "Cambiar archivo",
                key=key,
                on_click=al_cambiar,
                width="stretch"
            )
