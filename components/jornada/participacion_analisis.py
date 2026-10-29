import streamlit as st
import plotly.express as px


def mostrar_analisis_participacion(df):

    # --------------------------------------------------
    # CARRERAS REPRESENTADAS
    # --------------------------------------------------

    if "Investigador Carreras" in df.columns:

        carreras_completas = (
            df
            .drop_duplicates(subset="documento")
            .dropna(subset=["Investigador Carreras"])
            .groupby("Investigador Carreras")
            .size()
            .reset_index(name="participantes")
        )

        carreras = (
            carreras_completas
            .sort_values("participantes", ascending=False)
            .head(10)
            .sort_values("participantes", ascending=True)
        )

        if not carreras.empty:

            st.divider()

            st.markdown(
                "#### ¿Qué carreras estuvieron más representadas?"
            )

            st.caption(
                "Se muestra la cantidad de participantes únicos según la carrera "
                "informada. Se consideran únicamente los registros que contienen este dato."
            )

            fig_carreras = px.bar(
                carreras,
                x="participantes",
                y="Investigador Carreras",
                orientation="h",
                text="participantes"
            )

            fig_carreras.update_layout(
                xaxis_title="Participantes únicos",
                yaxis_title="",
                showlegend=False
            )

            st.plotly_chart(
                fig_carreras,
                use_container_width=True,
                key="grafico_carreras_participacion"
            )

            carrera_principal = (
                carreras_completas
                .sort_values("participantes", ascending=False)
                .iloc[0]
            )

            total_con_carrera = carreras_completas["participantes"].sum()

            porcentaje_carrera = (
                carrera_principal["participantes"]
                / total_con_carrera
                * 100
                if total_con_carrera > 0
                else 0
            )

            st.info(
                f"La carrera con mayor representación fue "
                f"**{carrera_principal['Investigador Carreras']}**, con "
                f"**{int(carrera_principal['participantes'])} participantes únicos** "
                f"({porcentaje_carrera:.1f}% de quienes informaron una carrera)."
            )

    # --------------------------------------------------
    # RELACIÓN ENTRE VARIABLES
    # --------------------------------------------------

    df_participantes = (
        df
        .drop_duplicates(subset="documento")
        .copy()
    )

    relaciones_disponibles = {}

    if (
        "Rol principal" in df_participantes.columns
        and "Miembro UNLa" in df_participantes.columns
    ):
        relaciones_disponibles[
            "¿Cómo se distribuyen los roles según la pertenencia a la UNLa?"
        ] = "Miembro UNLa"

    if (
        "Rol principal" in df_participantes.columns
        and "Tipo inscripción" in df_participantes.columns
    ):
        relaciones_disponibles[
            "¿Cómo se distribuyen los tipos de inscripción según el rol principal?"
        ] = "Tipo inscripción"

    if relaciones_disponibles:

        st.divider()

        st.markdown(
            "#### ¿Cómo se relacionan las principales características de los participantes?"
        )

        st.caption(
            "Se analizan participantes únicos y se cruzan dos variables "
            "para identificar las combinaciones más frecuentes."
        )

        relacion = st.selectbox(
            "Seleccioná una pregunta para analizar",
            list(relaciones_disponibles.keys()),
            key="relacion_participacion"
        )

        columna_cruce = relaciones_disponibles[relacion]

        roles_principales = (
            df_participantes
            .dropna(subset=["Rol principal"])
            .groupby("Rol principal")
            .size()
            .sort_values(ascending=False)
            .head(10)
            .index
        )

        cruce = (
            df_participantes
            .dropna(
                subset=[
                    "Rol principal",
                    columna_cruce
                ]
            )
        )

        cruce = cruce[
            cruce["Rol principal"].isin(roles_principales)
        ]

        cruce = (
            cruce
            .groupby(
                [
                    "Rol principal",
                    columna_cruce
                ]
            )
            .size()
            .reset_index(
                name="participantes"
            )
        )

        matriz = (
            cruce
            .pivot(
                index="Rol principal",
                columns=columna_cruce,
                values="participantes"
            )
            .fillna(0)
        )

        fig_matriz = px.imshow(
            matriz,
            text_auto=True,
            aspect="auto",
            labels={
                "x": columna_cruce,
                "y": "Rol principal",
                "color": "Participantes únicos"
            }
        )

        st.plotly_chart(
            fig_matriz,
            use_container_width=True,
            key="grafico_relacion_participacion"
        )

        if not cruce.empty:

            combinacion_principal = (
                cruce
                .sort_values(
                    "participantes",
                    ascending=False
                )
                .iloc[0]
            )

            cantidad = int(
                combinacion_principal["participantes"]
            )

            rol = combinacion_principal["Rol principal"]

            valor_cruce = combinacion_principal[columna_cruce]

            if columna_cruce == "Miembro UNLa":

                pertenencia = (
                    "pertenecen a la UNLa"
                    if str(valor_cruce).strip().lower() == "si"
                    else "no pertenecen a la UNLa"
                )

                st.info(
                    f"El cruce más frecuente corresponde a participantes con rol "
                    f"**{rol}** que **{pertenencia}**, con "
                    f"**{cantidad} participantes únicos**."
                )

            elif columna_cruce == "Tipo inscripción":

                st.info(
                    f"El cruce más frecuente corresponde a participantes con rol "
                    f"**{rol}** y tipo de inscripción "
                    f"**{valor_cruce}**, con "
                    f"**{cantidad} participantes únicos**."
                )