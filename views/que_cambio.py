import plotly.graph_objects as go
import streamlit as st

from components.ui import mostrar_origen_datos, selector_anio
from utils.metricas import tabla_que_cambio
from utils.grupos_categorias import agregar_grupos, cambios_de_definicion
from utils.historico_datos import cargar_historico
from utils.resumen_jornadas import (
    accion_sugerida,
    cambios_por_grupo,
    carreras_por_rol,
    formatear_numero,
    reencuentro,
    resumen_anual,
    roles_con_carrera,
    titular_cambios,
    titular_carreras,
)
from utils.tema import colores, estilo_figura


# --------------------------------------------------
# "QUÉ CAMBIÓ": diferencia por rol contra la edición anterior.
#   Nivel 1 -> titular + gráfico B + qué podemos hacer
#   Nivel 2 -> desglose por carrera dentro de un rol; ¿la gente vuelve?
#   Nivel 3 -> cómo se calcula
# --------------------------------------------------


def firmar(numero):

    numero = int(numero)

    if numero > 0:
        return f"+{formatear_numero(numero)}"

    if numero < 0:
        return f"−{formatear_numero(-numero)}"

    return "="


def mostrar_que_cambio():

    try:

        df_historico = agregar_grupos(cargar_historico())

    except Exception as error:

        st.title("Qué cambió")

        st.error(
            "No se pudo conectar con la base de datos del histórico. "
            "Probá de nuevo en unos minutos; si el problema persiste, "
            "puede ser un tema de configuración o de conexión."
        )

        with st.expander("Detalle técnico"):
            st.write(f"{type(error).__name__}: {error}")

        return

    anios = (
        resumen_anual(df_historico)["anio"].tolist()
        if not df_historico.empty
        else []
    )

    if len(anios) < 2:

        st.title("Qué cambió")

        st.info(
            "Para ver qué cambió hacen falta al menos dos jornadas "
            "guardadas en el histórico."
        )

        return

    # --------------------------------------------------
    # ENCABEZADO
    # --------------------------------------------------

    col_titulo, col_anio = st.columns([3, 1], vertical_alignment="bottom")

    with col_anio:
        anio = selector_anio(anios[1:], key="que_cambio_anio")

    anio_anterior = anios[anios.index(anio) - 1]

    with col_titulo:
        st.title(f"Qué cambió respecto de {anio_anterior}")
        st.caption(
            f"Diferencia de personas que vinieron, {anio} contra {anio_anterior}"
        )

    # --------------------------------------------------
    # NIVEL 1: TITULAR + GRÁFICO B + ACCIÓN
    # --------------------------------------------------

    st.subheader(titular_cambios(df_historico, anio_anterior, anio))

    # Si el formulario cambió las opciones de rol entre los dos años,
    # los grupos no significan exactamente lo mismo: se avisa y se
    # muestra qué cambió, plegado.
    definiciones = cambios_de_definicion(df_historico, anio_anterior, anio)

    if definiciones:

        st.warning(
            f"La comparación por grupo es aproximada: el formulario de "
            f"{anio} cambió las opciones de rol respecto de {anio_anterior}.",
            icon=":material/info:"
        )

        with st.expander("Qué cambió en el formulario"):

            for grupo, (antes, ahora) in definiciones.items():
                st.markdown(
                    f"- **{grupo}**: en {anio_anterior} "
                    + ", ".join(f"«{v}»" for v in antes)
                    + f"; en {anio} "
                    + ", ".join(f"«{v}»" for v in ahora)
                    + "."
                )

            st.caption(
                "Cada opción del formulario se asigna a un grupo para poder "
                "comparar años. Cuando cambian las opciones, una misma persona "
                "pudo haber elegido un grupo distinto (por ejemplo, un "
                "estudiante que trabaja)."
            )

    cambios = cambios_por_grupo(df_historico, anio_anterior, anio)

    if not cambios.empty:

        st.plotly_chart(
            grafico_cambios(cambios, anio_anterior, anio),
            use_container_width=True,
            key="grafico_cambios"
        )

    accion = accion_sugerida(df_historico, anio_anterior, anio)

    if accion:

        with st.container(border=True):
            st.markdown("**Qué podemos hacer**")
            st.write(accion)

    # --------------------------------------------------
    # NIVEL 2: CARRERA DENTRO DE UN ROL
    # --------------------------------------------------

    roles = roles_con_carrera(df_historico, anio)

    if roles:

        with st.expander("¿De qué carrera eran?"):

            rol = st.selectbox(
                "Ver dentro de",
                roles,
                key="que_cambio_rol"
            )

            tabla, total, sin_carrera, varias_carreras = carreras_por_rol(
                df_historico,
                anio_anterior,
                anio,
                rol
            )

            st.markdown(
                f"**{titular_carreras(tabla, total, sin_carrera, rol, anio_anterior)}**"
            )

            if not tabla.empty:

                st.plotly_chart(
                    grafico_carreras(tabla, anio_anterior, anio),
                    use_container_width=True,
                    key="grafico_carreras"
                )

            if varias_carreras > 0:

                st.caption(
                    f"{formatear_numero(varias_carreras)} "
                    f"persona{'' if varias_carreras == 1 else 's'} "
                    f"indic{'ó' if varias_carreras == 1 else 'aron'} más de "
                    "una carrera y cuenta en cada una, por eso la suma de las "
                    "barras puede ser mayor que el total del grupo."
                )

            if sin_carrera > 0:

                st.caption(
                    f"{formatear_numero(sin_carrera)} personas de este grupo "
                    "no indicaron carrera al inscribirse, así que no "
                    "aparecen en el gráfico."
                )

    # --------------------------------------------------
    # NIVEL 2: ¿LA GENTE VUELVE?
    # --------------------------------------------------

    with st.expander("¿La gente vuelve?"):
        st.write(reencuentro(df_historico, anio_anterior, anio))

    # --------------------------------------------------
    # NIVEL 3: ¿DE DÓNDE SALEN ESTOS NÚMEROS?
    # --------------------------------------------------

    mostrar_origen_datos(tabla_que_cambio(anio, anio_anterior))


def grafico_cambios(cambios, anio_anterior, anio):

    c = colores()

    grupos = cambios.index.tolist()
    diferencias = cambios["diferencia"].tolist()

    fig = go.Figure()

    fig.add_bar(
        y=grupos,
        x=diferencias,
        orientation="h",
        marker_color=[
            c["bajo"] if d < 0 else c["subio"] if d > 0 else c["datos_2"]
            for d in diferencias
        ],
        text=[firmar(d) for d in diferencias],
        textposition="outside",
        textfont_color=c["texto"],
        cliponaxis=False,
        customdata=list(zip(cambios[anio_anterior], cambios[anio])),
        hovertemplate=(
            f"%{{y}}<br>{anio_anterior}: %{{customdata[0]}} · "
            f"{anio}: %{{customdata[1]}}<extra></extra>"
        )
    )

    limite = max(abs(d) for d in diferencias) or 1

    fig.update_layout(
        barcornerradius=4,
        bargap=0.35,
        height=90 + 44 * len(grupos),
        showlegend=False
    )

    fig.update_xaxes(
        range=[-limite * 1.3, limite * 1.3],
        zeroline=True,
        zerolinewidth=1,
        showticklabels=False,
        title_text="▼ menos que en " + str(anio_anterior)
        + "          más que en " + str(anio_anterior) + " ▲"
    )

    # El grupo que más bajó queda arriba.
    fig.update_yaxes(autorange="reversed", title_text="", showgrid=False)

    estilo_figura(fig)

    fig.update_xaxes(zerolinecolor=c["eje"], showgrid=False)

    return fig


def grafico_carreras(tabla, anio_anterior, anio):

    c = colores()

    carreras = tabla.index.tolist()
    cantidades = tabla[anio].tolist()

    fig = go.Figure()

    fig.add_bar(
        y=carreras,
        x=cantidades,
        orientation="h",
        marker_color=[
            c["datos"] if i == 0 else c["datos_2"]
            for i in range(len(carreras))
        ],
        text=[
            f"{formatear_numero(n)} ("
            + (f"{firmar(d)} vs {anio_anterior}" if d else f"igual que en {anio_anterior}")
            + ")"
            for n, d in zip(cantidades, tabla["diferencia"])
        ],
        textposition="outside",
        textfont_color=c["texto"],
        cliponaxis=False,
        hovertemplate=(
            f"%{{y}}: %{{x}} en {anio}<extra></extra>"
        )
    )

    fig.update_layout(
        barcornerradius=4,
        bargap=0.35,
        height=70 + 40 * len(carreras),
        showlegend=False
    )

    fig.update_xaxes(
        range=[0, max(cantidades) * 1.6],
        showticklabels=False,
        title_text=""
    )

    fig.update_yaxes(autorange="reversed", title_text="", showgrid=False)

    estilo_figura(fig)

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)

    return fig
