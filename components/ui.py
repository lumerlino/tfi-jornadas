import html

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


def ir_a(pagina, texto):

    if st.button(texto, key=f"ir_a_{pagina}"):
        st.session_state["pagina"] = pagina
        st.rerun()
