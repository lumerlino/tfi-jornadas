import streamlit as st


# --------------------------------------------------
# PALETA "UNLa" PARA GRÁFICOS Y COMPONENTES PROPIOS
#
# Espejo de .streamlit/config.toml: Streamlit tematiza sus widgets
# solo, pero los colores de las trazas de Plotly se fijan desde
# Python, así que acá se elige el juego según el modo activo.
# Cada color cumple una sola función:
#   marca    -> franja superior y botones (nunca en gráficos)
#   datos    -> serie principal; datos_2 -> serie de referencia
#   bajo     -> disminución; subio -> aumento (siempre con ícono/signo)
#   atencion -> advertencias (siempre con ícono)
# --------------------------------------------------

COLORES = {
    "light": {
        "marca": "#7e0000",
        "fondo": "#fdf9f8",
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


def mostrar_encabezado():

    # Franja bordó con el nombre de la app, arriba del contenido.
    # Cuando haya un archivo del logo en el repo, se puede sumar
    # con st.logo() en la barra lateral.

    marca = COLORES["light"]["marca"]

    st.markdown(
        f"""
        <style>
        .encabezado-unla {{
            background: {marca};
            color: #ffffff;
            border-radius: 0.5rem;
            padding: 0.6rem 1rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: baseline;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}
        .encabezado-unla .titulo {{
            font-weight: 600;
            font-size: 1.05rem;
        }}
        .encabezado-unla .sub {{
            font-size: 0.85rem;
            opacity: 0.85;
        }}
        </style>
        <div class="encabezado-unla">
            <span class="titulo">Jornadas de Investigación</span>
            <span class="sub">Departamento de Desarrollo Productivo y Tecnológico · UNLa</span>
        </div>
        """,
        unsafe_allow_html=True
    )
