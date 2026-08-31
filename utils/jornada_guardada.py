import pandas as pd

from utils.guardado_historico import COLUMNAS_PARTICIPACIONES_INVERSO
from utils.historico_datos import cargar_registros


def _desempacar_datos_extra(df):

    if "datos_extra" not in df.columns:
        return df

    extras = df["datos_extra"].apply(
        lambda valor: valor if isinstance(valor, dict) else {}
    )

    df = df.drop(columns=["datos_extra"])

    df_extras = pd.json_normalize(extras)

    if df_extras.empty:
        return df

    return pd.concat(
        [df.reset_index(drop=True), df_extras.reset_index(drop=True)],
        axis=1
    )


def _obtener_asistencia_ancha(carga_id):

    # cargar_registros pagina de a 1000 filas (ver
    # utils/historico_datos.py) — necesario acá porque una jornada
    # de varios cientos de personas × varios días fácilmente supera
    # el límite de 1000 filas por página que impone Supabase.
    registros = cargar_registros("asistencias_dia", carga_id)

    if not registros:
        return pd.DataFrame()

    df = pd.DataFrame(registros)

    df["columna"] = "Asistencia " + df["fecha"]
    df["valor"] = df["asistio"].map({True: "Si", False: "No"})

    # pivot_table (no pivot): puede haber documentos duplicados
    # entre personas distintas (ya señalado en Calidad de datos),
    # y "pivot" no tolera índices repetidos — se toma el primer
    # valor en ese caso, sin intentar resolver la duplicación acá.
    return (
        df
        .pivot_table(
            index="documento",
            columns="columna",
            values="valor",
            aggfunc="first"
        )
        .reset_index()
    )


def reconstruir_jornada(carga_id):

    registros = cargar_registros("participaciones", carga_id)

    if not registros:
        return pd.DataFrame()

    df = pd.DataFrame(registros)

    df = df.rename(columns=COLUMNAS_PARTICIPACIONES_INVERSO)

    df = df.drop(
        columns=["id", "carga_id", "updated_at"],
        errors="ignore"
    )

    df = _desempacar_datos_extra(df)

    asistencia_ancha = _obtener_asistencia_ancha(carga_id)

    if not asistencia_ancha.empty:

        df = df.merge(
            asistencia_ancha,
            on="documento",
            how="left"
        )

    return df
