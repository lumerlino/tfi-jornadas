from pathlib import Path

import streamlit as st


# --------------------------------------------------
# PALETA "UNLa" PARA GRÁFICOS Y COMPONENTES PROPIOS
#
# Espejo de .streamlit/config.toml: Streamlit tematiza sus widgets
# solo, pero los colores de las trazas de Plotly se fijan desde
# Python, así que acá se elige el juego según el modo activo.
# Cada color cumple una sola función:
#   marca    -> franja superior, títulos de tarjetas y botones
#               (nunca en gráficos)
#   tarjeta  -> fondo de las tarjetas; sombra -> las hace "flotar"
#   datos    -> serie principal; datos_2 -> serie de referencia
#   bajo     -> disminución; subio -> aumento (siempre con ícono/signo)
#   atencion -> advertencias (siempre con ícono)
# --------------------------------------------------

COLORES = {
    "light": {
        "marca": "#7e0000",
        "fondo": "#f4efee",
        "tarjeta": "#ffffff",
        "sombra": "0 6px 18px rgba(60, 20, 20, 0.10), 0 1px 3px rgba(60, 20, 20, 0.08)",
        "sombra_hover": "0 10px 26px rgba(60, 20, 20, 0.18), 0 2px 6px rgba(60, 20, 20, 0.10)",
        "texto": "#0b0b0b",
        "texto_2": "#52514e",
        "texto_3": "#6f6d68",
        "grilla": "#e8e1de",
        "eje": "#c9c1be",
        "datos": "#383e45",
        "datos_2": "#aab0b7",
        "bajo": "#c2410c",
        "subio": "#256abf",
        "atencion": "#fab219",
    },
    "dark": {
        "marca": "#7e0000",
        "fondo": "#1b1918",
        "tarjeta": "#262322",
        "sombra": "0 6px 18px rgba(0, 0, 0, 0.45), 0 1px 3px rgba(0, 0, 0, 0.35)",
        "sombra_hover": "0 10px 26px rgba(0, 0, 0, 0.6), 0 2px 6px rgba(0, 0, 0, 0.4)",
        "texto": "#ffffff",
        "texto_2": "#c3c2b7",
        "texto_3": "#9a988f",
        "grilla": "#2e2a28",
        "eje": "#3e3937",
        "datos": "#b9bec6",
        "datos_2": "#4b5056",
        "bajo": "#d95926",
        "subio": "#3987e5",
        "atencion": "#fab219",
    },
}


def modo_actual():

    # st.context.theme.type puede venir en None en el primer
    # render, antes de que el navegador informe el tema.

    try:
        tipo = st.context.theme.type
    except Exception:
        tipo = None

    return tipo if tipo in COLORES else "light"


def colores():

    return COLORES[modo_actual()]


def estilo_figura(fig):

    # Grilla y ejes recesivos, leyenda arriba y hover unificado.
    # Los colores de las trazas los pone cada gráfico con colores().

    c = colores()

    fig.update_layout(
        # Transparente: el fondo lo pone la tarjeta que contiene al
        # gráfico (ver mostrar_marco).
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=36, b=8),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            title_text=""
        ),
        hoverlabel=dict(
            bgcolor=c["fondo"],
            bordercolor=c["eje"],
            font_color=c["texto"]
        ),
        font_color=c["texto_2"]
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor=c["eje"],
        tickfont_color=c["texto_3"]
    )

    fig.update_yaxes(
        gridcolor=c["grilla"],
        gridwidth=1,
        zeroline=False,
        linecolor=c["eje"],
        tickfont_color=c["texto_3"]
    )

    return fig


LOGO = Path(__file__).resolve().parent.parent / "assets" / "logo_jornadas.svg"

# Alto de la barra de Streamlit (header) en 1.51. La parte de arriba
# del menú lateral se pinta a la misma altura para que se lean como
# una sola barra de lado a lado.
ALTO_BARRA = "60px"

# Fondo del menú lateral: bordó más oscuro que la barra, para que la
# barra (identidad) y el menú (navegación) se distingan. Igual en
# claro y en oscuro.
MENU_FONDO = "#5c0000"



def mostrar_marco():

    # Identidad de la app: barra bordó continua arriba (barra de
    # Streamlit + parte superior del menú) con el nombre como logo.
    # Depende de data-testid internos (stHeader, stSidebar): si una
    # versión futura los cambia, la barra vuelve a verse neutra y el
    # logo sigue en el menú; no se rompe nada.

    st.logo(str(LOGO), size="large")

    marca = COLORES["light"]["marca"]
    claro = COLORES["light"]
    oscuro = COLORES["dark"]

    st.markdown(
        f"""
        <style>
        header[data-testid="stHeader"] {{
            background: {marca};
        }}
        header[data-testid="stHeader"] button,
        header[data-testid="stHeader"] [data-testid="stMainMenu"] {{
            color: #ffffff;
        }}
        [data-testid="stSidebar"] {{
            background-image: linear-gradient(
                to bottom,
                {marca} 0,
                {marca} {ALTO_BARRA},
                {MENU_FONDO} {ALTO_BARRA}
            );
        }}
        [data-testid="stSidebarHeader"] button {{
            color: #ffffff;
        }}

        /* Colores de tarjeta por modo en CSS y no desde Python:
           st.context.theme a veces informa el modo anterior y las
           tarjetas quedaban oscuras sobre la página clara. */
        :root {{
            --tarjeta: {claro["tarjeta"]};
            --sombra: {claro["sombra"]};
            --sombra-hover: {claro["sombra_hover"]};
        }}
        @media (prefers-color-scheme: dark) {{
            :root {{
                --tarjeta: {oscuro["tarjeta"]};
                --sombra: {oscuro["sombra"]};
                --sombra-hover: {oscuro["sombra_hover"]};
            }}
        }}

        /* ---------- TARJETAS ----------
           Todo el contenido flota en tarjetas con el mismo estilo:
           indicadores (st.metric con border=True), contenedores
           creados con tarjeta(), hallazgos, desplegables y gráficos.
           Título en franja bordó solo en los indicadores. */

        [data-testid="stMetric"],
        [class*="st-key-tarjeta_"],
        .hallazgo,
        [data-testid="stExpander"] details,
        [data-testid="stPlotlyChart"] {{
            background: var(--tarjeta);
            box-shadow: var(--sombra);
        }}
        [data-testid="stExpander"] details {{
            border-radius: 0.75rem;
        }}
        [data-testid="stPlotlyChart"] {{
            border-radius: 0.75rem;
            padding: 0.75rem;
        }}

        /* Un gráfico dentro de otra tarjeta no lleva la suya: no se
           apilan sombras. */
        [data-testid="stExpander"] [data-testid="stPlotlyChart"],
        [class*="st-key-tarjeta_"] [data-testid="stPlotlyChart"] {{
            background: transparent;
            box-shadow: none;
            padding: 0;
        }}
        [data-testid="stMetric"] {{
            overflow: hidden;
        }}
        [data-testid="stMetric"] > div {{
            padding: 0 0 0.9rem 0 !important;
        }}
        [data-testid="stMetricLabel"] {{
            display: flex;
            width: 100%;
            background: {marca};
            color: #ffffff;
            padding: 0.55rem 1rem;
            margin-bottom: 0.6rem;
        }}
        [data-testid="stMetricLabel"] p {{
            color: #ffffff;
        }}
        [data-testid="stMetricLabel"] svg {{
            stroke: rgba(255, 255, 255, 0.85) !important;
        }}
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"] {{
            padding: 0 1rem;
        }}

        /* ---------- ACCESOS EN MOSAICO ----------
           st.page_link dentro de un contenedor acceso_*: botón grande
           con ícono arriba, para ir a otra pantalla. */

        [class*="st-key-acceso_"] [data-testid="stElementContainer"],
        [class*="st-key-acceso_"] [data-testid="stPageLink"],
        [class*="st-key-acceso_"] [data-testid="stPageLink"] > div {{
            width: 100%;
        }}
        [class*="st-key-acceso_"] a {{
            width: 100%;
            flex-direction: column;
            justify-content: center;
            gap: 0.35rem;
            min-height: 5.5rem;
            background: {marca};
            border-radius: 0.6rem;
            box-shadow: var(--sombra);
            transition: box-shadow 0.15s ease, transform 0.15s ease;
        }}
        [class*="st-key-acceso_"] a:hover {{
            background: {marca};
            box-shadow: var(--sombra-hover);
            transform: translateY(-1px);
        }}
        [class*="st-key-acceso_"] a p,
        [class*="st-key-acceso_"] a span {{
            color: #ffffff !important;
            text-align: center;
        }}
        [class*="st-key-acceso_"] [data-testid="stIconMaterial"] {{
            font-size: 1.6rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
