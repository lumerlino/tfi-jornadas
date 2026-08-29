import streamlit as st


def mostrar_kpis_cruzados(df_historico):

    st.markdown("### KPIs cruzados: repetición entre ediciones")

    df_real = df_historico[~df_historico["es_demo"]]

    anios_reales = sorted(df_real["anio"].unique().tolist())

    if len(anios_reales) < 2:

        st.info(
            "Se necesitan al menos 2 ediciones reales (no de "
            "demostración) para calcular una tasa de repetición real. "
            f"Hoy hay {len(anios_reales)}."
        )

        return

    st.caption(
        "Se excluyen ediciones de demostración: esta métrica solo "
        "usa asistencia real entre ediciones consecutivas."
    )

    for anio_anterior, anio_siguiente in zip(
        anios_reales[:-1],
        anios_reales[1:]
    ):

        documentos_anterior = set(
            df_real[
                (df_real["anio"] == anio_anterior)
                & (df_real["asistio"])
            ]["documento"].dropna()
        )

        documentos_siguiente = set(
            df_real[
                (df_real["anio"] == anio_siguiente)
                & (df_real["asistio"])
            ]["documento"].dropna()
        )

        repiten = documentos_anterior & documentos_siguiente

        tasa_repeticion = (
            len(repiten) / len(documentos_anterior) * 100
            if documentos_anterior
            else 0
        )

        st.markdown(f"#### {anio_anterior} → {anio_siguiente}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                f"Asistentes {anio_anterior}",
                len(documentos_anterior)
            )

        with col2:
            st.metric(
                f"Volvieron en {anio_siguiente}",
                len(repiten)
            )

        with col3:
            st.metric(
                "Tasa de repetición",
                f"{tasa_repeticion:.1f}%"
            )

    st.divider()

    st.markdown("#### Relaciones que todavía no se pueden medir")

    st.write(
        "Una relación como 'más días de asistencia en una edición → "
        "mayor probabilidad de volver al año siguiente' necesita cruzar "
        "la asistencia día por día de una edición real contra la "
        "asistencia real de la edición siguiente. Con los datos "
        "actuales eso todavía no es posible: las ediciones reales más "
        "viejas no tienen desglose por día, y la edición más nueva con "
        "desglose por día todavía no tiene una edición real posterior "
        "con la que cruzarla. Va a poder calcularse en cuanto haya una "
        "tercera edición real cargada."
    )
