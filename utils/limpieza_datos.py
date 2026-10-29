import re

import pandas as pd


PATRON_ASISTENCIA = re.compile(r"^Asistencia \d{4}-\d{2}-\d{2}$")


def detectar_columnas_asistencia(df):

    return [
        columna
        for columna in df.columns
        if PATRON_ASISTENCIA.match(columna)
    ]


def reporte_calidad(df):

    nulos = df.isna().sum()

    return {
        "filas": len(df),
        "nulos_por_columna": nulos[nulos > 0],
        "duplicados": int(df.duplicated().sum())
    }


# ----------------------------------------------------
# 1. Normalización de texto
#   · Nombre/s, Apellido/s -> strip() + title()
#   · documento             -> strip()
#   · mail                  -> strip() + lower()
# ----------------------------------------------------

def normalizar_texto(df):

    df = df.copy()

    for columna in ["Nombre/s", "Apellido/s"]:

        if columna in df.columns:

            df[columna] = (
                df[columna]
                .astype(str)
                .str.strip()
                .str.title()
            )

    if "documento" in df.columns:

        # Excel sin decimales carga "documento" como float
        # cuando hay filas vacías (ej. 32134457.0); se limpia
        # el ".0" en vez de perder el valor con astype(str) directo.
        df["documento"] = df["documento"].apply(
            lambda valor: (
                pd.NA
                if pd.isna(valor)
                else str(valor)[:-2]
                if str(valor).endswith(".0")
                else str(valor).strip()
            )
        )

    if "mail" in df.columns:

        df["mail"] = (
            df["mail"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    return df


# ----------------------------------------------------
# 2. Reshape de asistencia: columnas anchas
#    "Asistencia YYYY-MM-DD" -> formato largo
#    (documento, fecha, asistio)
# ----------------------------------------------------

def construir_asistencia_larga(df, columnas_asistencia):

    asistencia_larga = df[
        ["documento"] + columnas_asistencia
    ].melt(
        id_vars="documento",
        value_vars=columnas_asistencia,
        var_name="fecha",
        value_name="asistio_texto"
    )

    asistencia_larga["fecha"] = pd.to_datetime(
        asistencia_larga["fecha"].str.replace(
            "Asistencia ", "", regex=False
        ),
        format="%Y-%m-%d"
    )

    asistencia_larga["asistio"] = (
        asistencia_larga["asistio_texto"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("si")
    )

    return asistencia_larga.drop(columns="asistio_texto")


def derivar_asistencia_jornada(asistencia_larga):

    return (
        asistencia_larga
        .groupby("documento")["asistio"]
        .any()
        .rename("asistio")
        .reset_index()
    )

def derivar_asistencia_por_fila(
        df,
        columnas_asistencia
    ):
        return (
            df[columnas_asistencia]
            .astype(str)
            .apply(
                lambda columna:
                    columna.str.strip().str.lower()
            )
            .eq("si")
            .any(axis=1)
        )


def comparar_asistencia_isPresent(
        df,
        asistencia_por_fila
    ):
        inconsistentes = (
            df["isPresent"].astype(bool)
            != asistencia_por_fila.astype(bool)
        )

        return int(inconsistentes.sum())


# ----------------------------------------------------
# Orquestador: aplica los pasos anteriores en orden
# y devuelve el DataFrame limpio, la asistencia en
# formato largo, y los reportes antes/después.
# ----------------------------------------------------

def limpiar_datos(df):

    reporte_antes = reporte_calidad(df)

    columnas_asistencia = detectar_columnas_asistencia(df)

    df_limpio = normalizar_texto(df)

    df_limpio = (
        df_limpio
        .drop_duplicates()
        .reset_index(drop=True)
    )

    if not columnas_asistencia:

        # Sin desglose de asistencia por día (ej. ediciones
        # viejas): isPresent es la única fuente disponible,
        # se usa directamente en vez de derivarla de un melt
        # vacío (que dejaría a todos como "no asistió").
        asistencia_larga = pd.DataFrame(
            columns=["documento", "fecha", "asistio"]
        )

        inconsistencias_asistencia = 0

        df_limpio = df_limpio.rename(
            columns={"isPresent": "isPresent_original"}
        )

        df_limpio["asistio"] = df_limpio["isPresent_original"]

    else:

        asistencia_larga = construir_asistencia_larga(
            df_limpio,
            columnas_asistencia
        )

        asistencia_por_fila = derivar_asistencia_por_fila(
            df_limpio,
            columnas_asistencia
        )

        inconsistencias_asistencia = comparar_asistencia_isPresent(
            df_limpio,
            asistencia_por_fila
        )

        asistencia_derivada = derivar_asistencia_jornada(
            asistencia_larga
        )

        df_limpio = df_limpio.rename(
            columns={"isPresent": "isPresent_original"}
        )

        df_limpio = df_limpio.merge(
            asistencia_derivada,
            on="documento",
            how="left"
        )

        df_limpio["asistio"] = (
            df_limpio["asistio"].fillna(False)
        )

    reporte_despues = reporte_calidad(df_limpio)
    reporte_despues["inconsistencias_asistencia"] = (
        inconsistencias_asistencia
    )
    reporte_despues["columnas_asistencia"] = columnas_asistencia

    return (
        df_limpio,
        asistencia_larga,
        reporte_antes,
        reporte_despues
    )
