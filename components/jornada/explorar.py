import streamlit as st
import pandas as pd
import plotly.express as px


def normalizar_booleano(valores):

    # "Tasa (%)" espera True/False reales. Muchas columnas
    # "booleanas" en realidad son texto tipo "Si"/"No" (así vienen
    # del Excel, ej. "Miembro UNLa") en vez de bool de Python —
    # se normalizan acá sin tocar el DataFrame original.

    if pd.api.types.is_bool_dtype(valores):
        return valores

    return (
        valores
        .astype(str)
        .str.strip()
        .str.lower()
        .map(
            {
                "si": True,
                "sí": True,
                "true": True,
                "no": False,
                "false": False
            }
        )
    )


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

        tasa = normalizar_booleano(valores).mean() * 100

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

    st.subheader("Variables adicionales del formulario")

    columnas_principales = {
        "Rol principal",
        "Miembro UNLa",
        "Tipo inscripción",
        "Source",
        "Investigador Carreras",
    }

    columnas_activas = [
        (columna, configuracion)
        for columna, configuracion in configuraciones.items()
        if columna in df.columns
        and columna not in columnas_principales
        and configuracion["metrica"] != "Ninguna"
    ]

    if not columnas_activas:

        st.info(
            "Esta jornada no tiene variables adicionales configuradas "
            "para mostrar en esta sección."
        )

        st.markdown(
            """
            Las **Variables adicionales** son datos que aparecen en el Excel
            pero que no forman parte de las columnas principales que la app
            ya conoce.

            Para visualizar una variable nueva en esta sección:

            1. Dirigite a **Preparar datos → Nueva jornada**.
            2. Cargá una jornada que incluya esa nueva columna en el Excel.
            3. Durante el paso **Revisar columnas nuevas**, configurá la variable.
            4. Elegí una visualización.
            5. Guardá la jornada en el histórico.
            6. Volvé a **Detalle de una jornada → Variables**.

            Las columnas principales se consultan en **Participación** y los
            registros completos de la jornada se pueden ver en **Datos**.
            """
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
