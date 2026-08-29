import streamlit as st
import plotly.express as px


def mostrar_escenarios(df_historico):

    st.markdown("### Simulación de escenarios (what-if)")

    ultimo_anio = df_historico["anio"].max()

    df_base = df_historico[df_historico["anio"] == ultimo_anio]

    st.caption(
        f"Simulación basada en la edición {int(ultimo_anio)}."
    )

    roles_disponibles = sorted(
        df_base["Rol principal"].dropna().unique().tolist()
    )

    if not roles_disponibles:

        st.info(
            "No hay datos de 'Rol principal' en la última edición "
            "para simular."
        )

        return

    rol_elegido = st.selectbox(
        "Segmento a mejorar",
        roles_disponibles,
        key="segmento_whatif"
    )

    mejora_pct = st.slider(
        "% de mejora en ese segmento",
        -50, 100, 10,
        key="mejora_whatif"
    )

    total_inscriptos = len(df_base)
    total_actual = int(df_base["asistio"].sum())

    asistentes_segmento = int(
        df_base[
            (df_base["Rol principal"] == rol_elegido)
            & (df_base["asistio"])
        ]
        .shape[0]
    )

    incremento = round(asistentes_segmento * mejora_pct / 100)

    total_simulado = max(0, total_actual + incremento)

    tasa_actual = total_actual / total_inscriptos * 100
    tasa_simulada = total_simulado / total_inscriptos * 100

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Asistentes totales",
            total_simulado,
            delta=f"{incremento:+d} vs. real"
        )

    with col2:

        st.metric(
            "Tasa de asistencia",
            f"{tasa_simulada:.1f}%",
            delta=f"{tasa_simulada - tasa_actual:+.1f} pts"
        )

    st.markdown("#### Composición por rol (real vs. simulado)")

    composicion = (
        df_base[df_base["asistio"]]
        .groupby("Rol principal")
        .size()
        .reset_index(name="Real")
    )

    composicion["Simulado"] = composicion["Real"]

    composicion.loc[
        composicion["Rol principal"] == rol_elegido,
        "Simulado"
    ] += incremento

    comparacion_larga = composicion.melt(
        id_vars="Rol principal",
        value_vars=["Real", "Simulado"],
        var_name="Escenario",
        value_name="Asistentes"
    )

    fig = px.bar(
        comparacion_larga,
        x="Rol principal",
        y="Asistentes",
        color="Escenario",
        barmode="group"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="grafico_whatif"
    )

    st.info(
        "Este simulador recalcula totales y composición a partir del "
        "porcentaje que elijas. La tasa de repetición entre ediciones "
        "**no se simula acá** porque depende de datos reales de personas "
        "que vuelven a asistir, no de un supuesto — se calcula en la "
        "pestaña de KPIs cruzados."
    )
