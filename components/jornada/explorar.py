import streamlit as st
import plotly.express as px


def mostrar_explorar(df, configuraciones):

    st.subheader("Explorar columnas nuevas")

    columnas_activas = [
        (columna, configuracion)
        for columna, configuracion in configuraciones.items()
        if columna in df.columns
        and configuracion["metrica"] != "Ninguna"
    ]

    if not columnas_activas:

        st.info(
            "Todavía no hay columnas nuevas configuradas con un "
            "gráfico activo. Si el Excel trae un campo que la app "
            "no reconoce, va a aparecer arriba del análisis para "
            "que elijas qué mostrar acá."
        )

        return


    for columna, configuracion in columnas_activas:

        nombre_display = configuracion["nombre_display"]
        metrica = configuracion["metrica"]

        st.markdown(f"#### {nombre_display}")

        if metrica == "Barras":

            conteo = (
                df[columna]
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
                key=f"grafico_explorar_barras_{columna}"
            )

        elif metrica == "Torta":

            conteo = (
                df[columna]
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
                key=f"grafico_explorar_torta_{columna}"
            )

        elif metrica == "Histograma":

            fig = px.histogram(
                df,
                x=columna
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f"grafico_explorar_histograma_{columna}"
            )

        elif metrica == "Resumen estadístico":

            st.dataframe(
                df[columna].describe().to_frame(),
                use_container_width=True
            )

        elif metrica == "Tasa (%)":

            tasa = df[columna].mean() * 100

            st.metric(
                f"{nombre_display} (Sí)",
                f"{tasa:.1f}%"
            )

        elif metrica == "Evolución temporal":

            conteo = (
                df
                .groupby(columna)
                .size()
                .reset_index(name="cantidad")
                .sort_values(columna)
            )

            fig = px.line(
                conteo,
                x=columna,
                y="cantidad",
                markers=True
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f"grafico_explorar_evolucion_{columna}"
            )

        st.divider()
