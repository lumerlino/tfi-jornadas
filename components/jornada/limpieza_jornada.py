import streamlit as st

from utils.transformaciones import preparar_datos


def preparar_y_mostrar_limpieza(df):
    df_original = df

    df, reporte_antes, reporte_despues = preparar_datos(df)

    with st.expander(
        "🧹 Ver reporte de limpieza de datos"
    ):
        filas_antes = reporte_antes["filas"]
        filas_despues = reporte_despues["filas"]

        filas_eliminadas = (
            filas_antes - filas_despues
        )

        duplicados_antes = (
            reporte_antes["duplicados"]
        )

        duplicados_despues = (
            reporte_despues["duplicados"]
        )

        duplicados_eliminados = max(
            duplicados_antes - duplicados_despues,
            0
        )

        st.markdown("#### Resultado de la limpieza")

        st.write(
            f"- **{filas_antes} registros** procesados."
        )

        st.write(
            f"- **{filas_eliminadas} filas** eliminadas durante la limpieza."
        )

        st.write(
            f"- **{duplicados_eliminados} duplicados** eliminados."
        )

        columnas_asistencia = (
            reporte_despues["columnas_asistencia"]
        )

        if columnas_asistencia:
            st.write(
                f"- Se detectaron **{len(columnas_asistencia)} columnas "
                f"de asistencia por día**."
            )

            inconsistencias = (
                reporte_despues["inconsistencias_asistencia"]
            )

            st.write(
                f"- Se detectaron **{inconsistencias} inconsistencias** "
                f"entre `isPresent` y la asistencia por día."
            )

        else:
            st.write(
                "- No se detectaron columnas de asistencia por día; "
                "se utiliza `isPresent` como fuente de asistencia."
            )

    return (
        df_original,
        df,
        reporte_antes,
        reporte_despues
    )