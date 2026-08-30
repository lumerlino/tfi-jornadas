import streamlit as st
import plotly.express as px


def renderizar_metrica(valores, nombre_display, metrica, key_prefix="explorar"):

    if metrica == "Barras":

        conteo = (
            valores
            .value_counts()
            .reset_index()
        )

        conteo.columns = [nombre_display, "cantidad"]

        fig = px.bar(
            conteo,
            x=nombre_display,
            y="cantidad",
            text="cantidad"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key=f"{key_prefix}_barras_{nombre_display}"
        )

    elif metrica == "Torta":

        conteo = (
            valores
            .value_counts()
            .reset_index()
        )

        conteo.columns = [nombre_display, "cantidad"]

        fig = px.pie(
            conteo,
            names=nombre_display,
            values="cantidad",
            hole=0.45
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key=f"{key_prefix}_torta_{nombre_display}"
        )

    elif metrica == "Histograma":

        fig = px.histogram(
            valores.to_frame(name=nombre_display),
            x=nombre_display
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key=f"{key_prefix}_histograma_{nombre_display}"
        )

    elif metrica == "Resumen estadístico":

        st.dataframe(
            valores.describe().to_frame(),
            use_container_width=True
        )

    elif metrica == "Tasa (%)":

        tasa = valores.mean() * 100

        st.metric(
            f"{nombre_display} (Sí)",
            f"{tasa:.1f}%"
        )

    elif metrica == "Evolución temporal":

        conteo = (
            valores
            .to_frame(name=nombre_display)
            .groupby(nombre_display)
            .size()
            .reset_index(name="cantidad")
            .sort_values(nombre_display)
        )

        fig = px.line(
            conteo,
            x=nombre_display,
            y="cantidad",
            markers=True
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key=f"{key_prefix}_evolucion_{nombre_display}"
        )

    else:

        st.info(f"Métrica '{metrica}' sin gráfico asociado.")


def mostrar_explorar(df, configuraciones):

    st.subheader("Explorar columnas configuradas")

    columnas_activas = [
        (columna, configuracion)
        for columna, configuracion in configuraciones.items()
        if columna in df.columns
        and configuracion["metrica"] != "Ninguna"
    ]

    if not columnas_activas:

        st.info(
            "No hay ninguna columna configurada con un gráfico "
            "activo todavía (ni de las oficiales ni de las nuevas). "
            "Se configuran desde 'Columnas nuevas detectadas' más "
            "arriba, o se editan en la página ⚙️ Configuración."
        )

        return


    for columna, configuracion in columnas_activas:

        nombre_display = configuracion["nombre_display"]
        metrica = configuracion["metrica"]

        st.markdown(f"#### {nombre_display}")

        renderizar_metrica(
            df[columna],
            nombre_display,
            metrica,
            key_prefix="explorar"
        )

        st.divider()
