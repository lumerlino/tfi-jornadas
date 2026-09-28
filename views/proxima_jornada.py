import plotly.graph_objects as go
import streamlit as st

from utils.grupos_categorias import agregar_grupos
from utils.historico_datos import cargar_historico
from utils.resumen_jornadas import (
    aprendizajes,
    estimacion,
    formatear_numero,
    redondear_a_10,
    resumen_anual,
    titular_meta,
)
from utils.tema import colores, estilo_figura


# --------------------------------------------------
# "NUESTRA PRÓXIMA JORNADA": siempre a partir de la última edición.
#   Nivel 1 -> meta (superar la última) + titular + gráfico C
#              + lo que aprendimos de otros años
#   Nivel 2 -> cambiar la meta
#   Nivel 3 -> método y confianza de la estimación
# --------------------------------------------------

# La meta elegida vive fuera del widget: el estado de un widget se
# borra al cambiar de pantalla y la meta tiene que sobrevivir.
CLAVE_META = "meta_proxima_jornada"
CLAVE_WIDGET_META = "meta_proxima_jornada_input"


def _guardar_meta():

    st.session_state[CLAVE_META] = st.session_state[CLAVE_WIDGET_META]


def _restablecer_meta(meta_automatica):

    st.session_state[CLAVE_META] = meta_automatica
    st.session_state.pop(CLAVE_WIDGET_META, None)


def mostrar_proxima_jornada():

    try:

        df_historico = agregar_grupos(cargar_historico())

    except Exception as error:

        st.title("Nuestra próxima jornada")

        st.error(
            "No se pudo conectar con la base de datos del histórico. "
            "Probá de nuevo en unos minutos; si el problema persiste, "
            "puede ser un tema de configuración o de conexión."
        )

        with st.expander("Detalle técnico"):
            st.write(f"{type(error).__name__}: {error}")

        return

    if df_historico.empty:

        st.title("Nuestra próxima jornada")

        st.info(
            "Todavía no hay jornadas guardadas. Con la primera ya vamos a "
            "tener una meta para superar."
        )

        return

    resumen = resumen_anual(df_historico)

    ultima = resumen.iloc[-1]
    anio = int(ultima["anio"])
    vinieron = int(ultima["vinieron"])
    proximo = anio + 1

    tendencia = estimacion(resumen)

    # La meta por defecto es superar la última edición. Si la persona
    # la cambió (nivel 2), el valor vive en session_state.
    meta_automatica = vinieron
    meta = int(st.session_state.get(CLAVE_META, meta_automatica))
    es_automatica = meta == meta_automatica

    st.title("Nuestra próxima jornada")
    st.caption(
        f"Estimación para {proximo} a partir de "
        f"{len(resumen)} edicion{'' if len(resumen) == 1 else 'es'}"
    )

    # --------------------------------------------------
    # NIVEL 1: META + TITULAR + GRÁFICO C
    # --------------------------------------------------

    with st.container(border=True):

        if es_automatica:
            st.markdown(
                f"**Meta: superar las {formatear_numero(meta)} personas de "
                f"{anio}**  \n:gray[Meta automática: superar la última jornada]"
            )
        else:
            st.markdown(
                f"**Meta: superar las {formatear_numero(meta)} personas**  \n"
                ":gray[Meta elegida por nosotros]"
            )

    st.subheader(titular_meta(tendencia, meta, anio, vinieron))

    st.plotly_chart(
        grafico_proxima(resumen, tendencia, meta),
        use_container_width=True,
        key="grafico_proxima"
    )

    st.caption(
        "Línea llena: personas que vinieron. Línea punteada: hacia dónde "
        "vamos si nada cambia. Línea de puntos horizontal: la meta."
    )

    lista = aprendizajes(df_historico)

    if lista:

        st.subheader("Lo que aprendimos de otros años")

        for texto in lista:
            st.markdown(f"- {texto}")

    # --------------------------------------------------
    # NIVEL 2: CAMBIAR LA META
    # --------------------------------------------------

    with st.expander("Cambiar la meta"):

        st.number_input(
            f"Personas que queremos superar en {proximo}",
            min_value=1,
            step=10,
            value=meta,
            key=CLAVE_WIDGET_META,
            on_change=_guardar_meta
        )

        if not es_automatica:
            st.button(
                f"Volver a la meta automática ({formatear_numero(meta_automatica)})",
                on_click=_restablecer_meta,
                args=(meta_automatica,)
            )

    # --------------------------------------------------
    # NIVEL 3: DETALLE TÉCNICO
    # --------------------------------------------------

    with st.expander("Detalle técnico"):

        if tendencia["suficiente"]:

            r2 = f"{tendencia['r2']:.2f}".replace(".", ",")

            st.markdown(
                f"- Regresión lineal sobre {tendencia['anios_disponibles']} "
                f"ediciones ({int(resumen['anio'].iloc[0])}–{anio}).\n"
                f"- Estimación {proximo}: {tendencia['proyeccion']:.0f} "
                f"personas (en el titular se redondea a "
                f"{formatear_numero(redondear_a_10(tendencia['proyeccion']))}).\n"
                f"- R² = {r2}: cuánto de la variación entre años explica la "
                "línea. Con pocas ediciones la confianza es baja; es "
                "orientativo, no una predicción."
            )

        else:

            st.markdown(
                f"- La estimación necesita al menos "
                f"{tendencia['anios_necesarios']} ediciones; hoy hay "
                f"{tendencia['anios_disponibles']}."
            )


def grafico_proxima(resumen, tendencia, meta):

    c = colores()

    anios = resumen["anio"].tolist()
    vinieron = resumen["vinieron"].tolist()

    fig = go.Figure()

    if tendencia["suficiente"]:

        proximo = tendencia["proximo_anio"]
        extremos = [anios[0], proximo]

        fig.add_scatter(
            x=extremos,
            y=[tendencia["pendiente"] * a + tendencia["ordenada"] for a in extremos],
            mode="lines",
            name="Si nada cambia",
            line=dict(color=c["texto_3"], width=2, dash="dash"),
            hoverinfo="skip"
        )

        estimado = redondear_a_10(tendencia["proyeccion"])

        fig.add_scatter(
            x=[proximo],
            y=[tendencia["proyeccion"]],
            mode="markers+text",
            name=f"Estimación {proximo}",
            marker=dict(
                size=13,
                color=c["fondo"],
                line=dict(color=c["datos"], width=2.5)
            ),
            text=[f"≈ {formatear_numero(estimado)}"],
            textposition="top center",
            textfont_color=c["texto"],
            hovertemplate=f"{proximo} estimado: unas {formatear_numero(estimado)}<extra></extra>"
        )

    fig.add_scatter(
        x=anios,
        y=vinieron,
        mode="lines+markers+text",
        name="Vinieron",
        line=dict(color=c["datos"], width=2),
        marker=dict(size=9, color=c["datos"], line=dict(color=c["fondo"], width=2)),
        text=[formatear_numero(v) if i == len(anios) - 1 else "" for i, v in enumerate(vinieron)],
        textposition="bottom center",
        textfont_color=c["texto"],
        hovertemplate="%{x}: vinieron %{y}<extra></extra>"
    )

    fig.add_hline(
        y=meta,
        line=dict(color=c["texto_2"], width=1.5, dash="dot"),
        annotation_text=f"Meta: más de {formatear_numero(meta)}",
        annotation_position="top left",
        annotation_font_color=c["texto_2"]
    )

    ticks = anios + ([tendencia["proximo_anio"]] if tendencia["suficiente"] else [])

    fig.update_layout(height=380)

    fig.update_xaxes(
        tickmode="array",
        tickvals=ticks,
        ticktext=[
            f"{a} (est.)" if tendencia["suficiente"] and a == tendencia["proximo_anio"] else str(a)
            for a in ticks
        ],
        title_text=""
    )

    fig.update_yaxes(title_text="Personas", rangemode="tozero")

    return estilo_figura(fig)
