import streamlit as st
import plotly.express as px


def mostrar_perfil_participantes(df_participantes):

    tiene_rol = "Rol principal" in df_participantes.columns
    tiene_unla = "Miembro UNLa" in df_participantes.columns
    tiene_tipo_inscripcion = "Tipo inscripción" in df_participantes.columns
    tiene_source = "Source" in df_participantes.columns


    # --------------------------------------------------
    # PARTICIPANTES POR ROL
    # --------------------------------------------------

    if tiene_rol:

        st.markdown(
            "#### ¿Qué roles tuvieron mayor participación?"
        )

        st.caption(
            "Se muestra la cantidad de participantes únicos según el rol "
            "principal informado al momento de la inscripción."
        )

        participacion_rol = (
            df_participantes
            .dropna(subset=["Rol principal"])
            .groupby("Rol principal")
            .size()
            .reset_index(name="participantes")
            .sort_values(
                "participantes",
                ascending=True
            )
        )

        fig_rol = px.bar(
            participacion_rol,
            x="participantes",
            y="Rol principal",
            orientation="h",
            text="participantes"
        )

        fig_rol.update_layout(
            xaxis_title="Participantes únicos",
            yaxis_title="",
            showlegend=False
        )

        st.plotly_chart(
            fig_rol,
            use_container_width=True,
            key="grafico_participacion_rol"
        )

        if not participacion_rol.empty:

            rol_mayor = participacion_rol.iloc[-1]

            total_con_rol = (
                participacion_rol["participantes"].sum()
            )

            porcentaje_rol = (
                rol_mayor["participantes"]
                / total_con_rol
                * 100
                if total_con_rol > 0
                else 0
            )

            st.info(
                f"El rol con mayor participación fue "
                f"**{rol_mayor['Rol principal']}**, con "
                f"**{int(rol_mayor['participantes'])} participantes únicos** "
                f"({porcentaje_rol:.1f}% de quienes informaron un rol)."
            )


    # --------------------------------------------------
    # CARACTERÍSTICAS GENERALES
    # --------------------------------------------------

    if tiene_unla or tiene_tipo_inscripcion or tiene_source:

        st.divider()

        st.markdown(
            "#### ¿Cómo se caracterizan los participantes?"
        )

        st.caption(
            "Se muestran algunas características generales de los participantes únicos "
            "a partir de la información registrada en la inscripción."
        )

        col1, col2, col3 = st.columns(3)


        # --------------------------------------------------
        # MIEMBRO UNLA
        # --------------------------------------------------

        with col1:

            if tiene_unla:

                st.markdown(
                    "##### Pertenencia a la UNLa"
                )

                participacion_unla = (
                    df_participantes
                    .dropna(subset=["Miembro UNLa"])
                    .groupby("Miembro UNLa")
                    .size()
                    .reset_index(name="participantes")
                )

                participacion_unla["pertenencia"] = (
                    participacion_unla["Miembro UNLa"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .map({
                        "si": "Miembro UNLa",
                        "no": "No miembro UNLa"
                    })
                )

                participacion_unla = participacion_unla[
                    participacion_unla["pertenencia"].notna()
                ]

                total_unla = (
                    participacion_unla["participantes"].sum()
                )

                fila_unla = participacion_unla[
                    participacion_unla["pertenencia"] == "Miembro UNLa"
                ]

                miembros_unla = (
                    int(fila_unla["participantes"].iloc[0])
                    if not fila_unla.empty
                    else 0
                )

                porcentaje_unla = (
                    miembros_unla / total_unla * 100
                    if total_unla > 0
                    else 0
                )

                fig_unla = px.pie(
                    participacion_unla,
                    names="pertenencia",
                    values="participantes",
                    hole=0.45
                )

                fig_unla.update_traces(
                    textposition="inside",
                    textinfo="label+percent"
                )

                fig_unla.update_layout(
                    showlegend=False
                )

                st.plotly_chart(
                    fig_unla,
                    use_container_width=True,
                    key="grafico_perfil_participantes"
                )

                st.info(
                    f"El **{porcentaje_unla:.1f}%** pertenece a la UNLa "
                    f"(**{miembros_unla} participantes únicos**)."
                )


        # --------------------------------------------------
        # TIPO DE INSCRIPCIÓN
        # --------------------------------------------------

        with col2:

            if tiene_tipo_inscripcion:

                st.markdown(
                    "##### Tipo de inscripción"
                )

                participacion_tipo = (
                    df_participantes
                    .dropna(subset=["Tipo inscripción"])
                    .groupby("Tipo inscripción")
                    .size()
                    .reset_index(name="participantes")
                )

                fig_tipo = px.pie(
                    participacion_tipo,
                    names="Tipo inscripción",
                    values="participantes",
                    hole=0.45
                )

                fig_tipo.update_traces(
                    textposition="inside",
                    textinfo="label+percent"
                )

                fig_tipo.update_layout(
                    showlegend=False
                )

                st.plotly_chart(
                    fig_tipo,
                    use_container_width=True,
                    key="grafico_tipo_inscripcion"
                )

                if not participacion_tipo.empty:

                    tipo_principal = (
                        participacion_tipo
                        .sort_values(
                            "participantes",
                            ascending=False
                        )
                        .iloc[0]
                    )

                    total_tipo = (
                        participacion_tipo["participantes"].sum()
                    )

                    porcentaje_tipo = (
                        tipo_principal["participantes"]
                        / total_tipo
                        * 100
                        if total_tipo > 0
                        else 0
                    )

                    st.info(
                        f"Predominó **{tipo_principal['Tipo inscripción']}**, "
                        f"con **{int(tipo_principal['participantes'])} participantes únicos** "
                        f"({porcentaje_tipo:.1f}%)."
                    )


        # --------------------------------------------------
        # SOURCE
        # --------------------------------------------------

        with col3:

            if tiene_source:

                st.markdown(
                    "##### Origen del registro"
                )

                participacion_source = (
                    df_participantes
                    .dropna(subset=["Source"])
                    .groupby("Source")
                    .size()
                    .reset_index(name="participantes")
                )

                fig_source = px.pie(
                    participacion_source,
                    names="Source",
                    values="participantes",
                    hole=0.45
                )

                fig_source.update_traces(
                    textposition="inside",
                    textinfo="label+percent"
                )

                fig_source.update_layout(
                    showlegend=False
                )

                st.plotly_chart(
                    fig_source,
                    use_container_width=True,
                    key="grafico_source_participacion"
                )

                if not participacion_source.empty:

                    source_principal = (
                        participacion_source
                        .sort_values(
                            "participantes",
                            ascending=False
                        )
                        .iloc[0]
                    )

                    total_source = (
                        participacion_source["participantes"].sum()
                    )

                    porcentaje_source = (
                        source_principal["participantes"]
                        / total_source
                        * 100
                        if total_source > 0
                        else 0
                    )

                    st.info(
                        f"El origen más frecuente fue "
                        f"**{source_principal['Source']}**, con "
                        f"**{int(source_principal['participantes'])} participantes únicos** "
                        f"({porcentaje_source:.1f}%)."
                    )