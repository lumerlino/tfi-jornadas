import plotly.graph_objects as go
import streamlit as st

from components.navegacion import acceso, ir_a
from components.ui import mostrar_hallazgos, mostrar_origen_datos, selector_anio
from utils.metricas import (
    ayuda,
    fuente_asistencia,
    paso_a_paso_historico,
    tabla_como_nos_fue,
)
from utils.grupos_categorias import agregar_grupos
from utils.historico_datos import cargar_historico
from utils.resumen_jornadas import (
    de_cada_10,
    formatear_numero,
    hallazgos,
    resumen_anual,
    variacion_porcentual,
    volvieron,
)
from utils.tema import colores, estilo_figura


# --------------------------------------------------
# "CÓMO NOS FUE": pantalla de inicio del MVP.
#   Nivel 1 -> tres números comparados + tres hallazgos en frases
#   Nivel 2 -> gráfico A (inscriptos vs. vinieron por año)
#   Nivel 3 -> cómo se calcula cada número
# --------------------------------------------------


def mostrar_como_nos_fue():

    try:

        df_historico = agregar_grupos(cargar_historico())

    except Exception as error:

        st.title("Cómo nos fue")

        st.error(
            "No se pudo conectar con la base de datos del histórico. "
            "Probá de nuevo en unos minutos; si el problema persiste, "
            "puede ser un tema de configuración o de conexión."
        )

        with st.expander("Detalle técnico"):
            st.write(f"{type(error).__name__}: {error}")

        return

    if df_historico.empty:

        st.title("Cómo nos fue")

        st.info(
            "Todavía no hay jornadas guardadas. Cuando carguemos la "
            "primera, acá vamos a ver cómo nos fue."
        )

        ir_a("cargar_jornada", "Cargar una jornada")

        return

    resumen = resumen_anual(df_historico)
    anios = resumen["anio"].tolist()

    # --------------------------------------------------
    # ENCABEZADO: abre siempre en la última jornada
    # --------------------------------------------------

    col_titulo, col_anio = st.columns([3, 1], vertical_alignment="bottom")

    with col_anio:

        anio = selector_anio(anios, key="como_nos_fue_anio")

    posicion = anios.index(anio)
    fila = resumen.iloc[posicion]
    fila_anterior = resumen.iloc[posicion - 1] if posicion > 0 else None

    with col_titulo:

        st.title(f"Cómo nos fue en {anio}")

        if fila_anterior is not None:
            st.caption(f"Jornada {anio} comparada con {int(fila_anterior['anio'])}")
        else:
            st.caption(f"Jornada {anio}")

    # --------------------------------------------------
    # NIVEL 1: TRES NÚMEROS, SIEMPRE COMPARADOS
    # --------------------------------------------------

    mostrar_indicadores(df_historico, fila, fila_anterior)

    if fila_anterior is None:

        st.info(
            "Es la primera jornada del histórico: cuando carguemos otra, "
            "vamos a poder comparar."
        )

    else:

        col_hallazgos, col_accesos = st.columns([2, 1], gap="medium")

        with col_hallazgos:

            st.subheader("Lo más importante")

            mostrar_hallazgos(hallazgos(df_historico, anio))

        with col_accesos:

            st.subheader("Seguir por")

            col_cambio, col_proxima = st.columns(2)

            with col_cambio:
                acceso("que_cambio", "Qué cambió", ":material/compare_arrows:")

            with col_proxima:
                acceso("proxima_jornada", "Próxima jornada", ":material/flag:")

    # --------------------------------------------------
    # NIVEL 2: GRÁFICO A
    # --------------------------------------------------

    with st.expander("Nuestra audiencia en los últimos años"):

        st.plotly_chart(
            grafico_audiencia(resumen, anio),
            use_container_width=True,
            key="grafico_audiencia"
        )

        st.caption(
            "Barra clara: se anotaron. Barra oscura: vinieron. "
            f"{anio} está resaltado."
        )

    # --------------------------------------------------
    # NIVEL 3: ¿DE DÓNDE SALEN ESTOS NÚMEROS?
    # --------------------------------------------------

    df_anio = df_historico[df_historico["anio"] == anio]
    fuente = fuente_asistencia(df_anio)
    anio_anterior = int(fila_anterior["anio"]) if fila_anterior is not None else None

    mostrar_origen_datos(
        tabla_como_nos_fue(fuente, anio, anio_anterior),
        pasos=paso_a_paso_historico(df_anio, fuente),
        titulo_pasos=f"Cómo se llegó a «Vinieron» en {anio}"
    )


def mostrar_indicadores(df_historico, fila, fila_anterior):

    fuente = fuente_asistencia(df_historico[df_historico["anio"] == fila["anio"]])

    vinieron = int(fila["vinieron"])
    inscriptos = int(fila["inscriptos"])
    proporcion = de_cada_10(vinieron, inscriptos)

    col1, col2, col3 = st.columns(3)

    if fila_anterior is None:

        with col1:
            st.metric(
                "Vinieron",
                formatear_numero(vinieron),
                border=True,
                help=ayuda("vinieron", fuente)
            )

        with col2:
            st.metric(
                "De cada 10 inscriptos",
                f"{proporcion} vinieron",
                border=True,
                help=ayuda("de_cada_10")
            )

        with col3:
            st.metric(
                "Se anotaron",
                formatear_numero(inscriptos),
                border=True,
                help=ayuda("se_anotaron")
            )

        return

    anio_anterior = int(fila_anterior["anio"])
    vinieron_antes = int(fila_anterior["vinieron"])
    proporcion_antes = de_cada_10(vinieron_antes, int(fila_anterior["inscriptos"]))

    variacion = variacion_porcentual(vinieron, vinieron_antes)

    with col1:

        st.metric(
            "Vinieron",
            formatear_numero(vinieron),
            delta=(
                f"{variacion:+.0f} % vs {anio_anterior} "
                f"({formatear_numero(vinieron_antes)})"
                if variacion is not None
                else None
            ),
            border=True,
            help=ayuda("vinieron", fuente)
        )

    with col2:

        diferencia = proporcion - proporcion_antes

        st.metric(
            "De cada 10 inscriptos",
            f"{proporcion} vinieron",
            delta=(
                f"{diferencia:+d} vs {anio_anterior} (antes {proporcion_antes})"
                if diferencia != 0
                else None
            ),
            border=True,
            help=(
                ayuda("de_cada_10")
                + (f" Igual que en {anio_anterior}." if diferencia == 0 else "")
            )
        )

    with col3:

        cantidad, porcentaje = volvieron(
            df_historico,
            anio_anterior,
            int(fila["anio"])
        )

        # Sin delta: no es una variación, y st.metric le pondría
        # una flecha que no significa nada.
        st.metric(
            f"Volvieron de {anio_anterior}",
            formatear_numero(cantidad),
            border=True,
            help=ayuda("volvieron", anio_anterior=anio_anterior)
        )

        st.caption(f"{porcentaje:.0f} % de quienes vinieron en {anio_anterior}")


def grafico_audiencia(resumen, anio):

    c = colores()

    anios = resumen["anio"].tolist()

    # El año elegido va a color pleno; el resto, atenuado.
    opacidad = [1 if a == anio else 0.45 for a in anios]

    texto_inscriptos = [
        formatear_numero(v) if a == anio else ""
        for a, v in zip(anios, resumen["inscriptos"])
    ]

    texto_vinieron = [
        formatear_numero(v) if a == anio else ""
        for a, v in zip(anios, resumen["vinieron"])
    ]

    proporciones = [
        de_cada_10(v, i)
        for v, i in zip(resumen["vinieron"], resumen["inscriptos"])
    ]

    fig = go.Figure()

    fig.add_bar(
        x=anios,
        y=resumen["inscriptos"],
        name="Se anotaron",
        marker=dict(color=c["datos_2"], opacity=opacidad),
        text=texto_inscriptos,
        textposition="outside",
        hovertemplate="%{x}: se anotaron %{y}<extra></extra>"
    )

    fig.add_bar(
        x=anios,
        y=resumen["vinieron"],
        name="Vinieron",
        marker=dict(color=c["datos"], opacity=opacidad),
        text=texto_vinieron,
        textposition="outside",
        customdata=proporciones,
        hovertemplate=(
            "%{x}: vinieron %{y} (%{customdata} de cada 10)<extra></extra>"
        )
    )

    fig.update_layout(
        barmode="group",
        bargap=0.35,
        bargroupgap=0.08,
        barcornerradius=4,
        height=340
    )

    fig.update_xaxes(tickmode="array", tickvals=anios, title_text="")
    fig.update_yaxes(title_text="Personas", rangemode="tozero")

    fig.update_traces(textfont_color=c["texto"], cliponaxis=False)

    return estilo_figura(fig)
