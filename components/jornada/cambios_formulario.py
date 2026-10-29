import streamlit as st

from utils.historico_datos import cargar_historico
from utils.configuracion_columnas import (
    obtener_configuraciones,
    CONFIGURACION_POR_DEFECTO,
)


def mostrar_cambios_formulario(df, metadatos):

    anio = (metadatos or {}).get("anio")

    if anio is None:
        return

    try:
        historico = cargar_historico()
    except Exception:
        return

    if historico.empty:
        return

    anteriores = sorted(
        a
        for a in historico["anio"].dropna().unique()
        if a < anio
    )

    if not anteriores:
        return

    anio_anterior = int(
        anteriores[-1]
    )

    try:
        configuraciones = obtener_configuraciones()
    except Exception:
        configuraciones = CONFIGURACION_POR_DEFECTO

    columnas_comparables = [
        columna
        for columna, configuracion in configuraciones.items()
        if configuracion.get("tipo_dato") in ("categorica", "booleana")
        and columna in df.columns
        and columna in historico.columns
    ]

    historico_anterior = historico[
        historico["anio"] == anio_anterior
    ]

    cambios = []

    for columna in columnas_comparables:

        valores_anteriores = {
            str(valor).strip()
            for valor in historico_anterior[columna].dropna().unique()
            if str(valor).strip()
        }

        valores_actuales = {
            str(valor).strip()
            for valor in df[columna].dropna().unique()
            if str(valor).strip()
        }

        nuevos = sorted(
            valores_actuales - valores_anteriores
        )

        no_presentes = sorted(
            valores_anteriores - valores_actuales
        )

        if nuevos or no_presentes:

            configuracion = configuraciones[columna]

            nombre = configuracion.get(
                "nombre_display",
                columna
            )

            cambios.append(
                {
                    "columna": columna,
                    "nombre": nombre,
                    "nuevos": nuevos,
                    "no_presentes": no_presentes,
                }
            )

    if not cambios:
        return

    st.info(
        f"Se detectaron diferencias en algunos valores registrados "
        f"respecto de {anio_anterior}. "
        "La jornada se puede guardar normalmente. "
        "Estas diferencias pueden influir en algunas comparaciones "
        "entre años.",
        icon=":material/info:"
    )

    with st.expander("Ver diferencias detectadas"):

        for cambio in cambios:

            st.markdown(f"### {cambio['nombre']}")

            cantidad_nuevos = len(cambio["nuevos"])
            cantidad_no_presentes = len(cambio["no_presentes"])

            st.caption(
                f"{cantidad_nuevos} valores nuevos · "
                f"{cantidad_no_presentes} valores que ya no aparecen "
                f"respecto de {anio_anterior}"
            )

            col_nuevos, col_anteriores = st.columns(2)

            with col_nuevos:
                st.markdown("**Nuevos en esta jornada**")

                if cambio["nuevos"]:
                    for valor in cambio["nuevos"]:
                        st.write(f"• {valor}")
                else:
                    st.caption("Sin valores nuevos.")

            with col_anteriores:
                st.markdown(
                    f"**Ya no aparecen respecto de {anio_anterior}**"
                )

                if cambio["no_presentes"]:
                    for valor in cambio["no_presentes"]:
                        st.write(f"• {valor}")
                else:
                    st.caption("Sin diferencias.")

            st.divider()