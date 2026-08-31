import pandas as pd

from utils.supabase_cliente import obtener_cliente_supabase
from utils.guardado_historico import COLUMNAS_PARTICIPACIONES_INVERSO


def obtener_ultima_carga_por_jornada():

    supabase = obtener_cliente_supabase()

    respuesta = (
        supabase
        .table("cargas")
        .select("id, jornada_id, numero_carga, fecha_carga")
        .order("numero_carga", desc=True)
        .execute()
    )

    cargas = respuesta.data

    ultimas_cargas = {}

    for carga in cargas:

        jornada_id = carga["jornada_id"]

        if jornada_id not in ultimas_cargas:
            ultimas_cargas[jornada_id] = carga

    return ultimas_cargas


def cargar_registros(tabla, carga_id, tamanio_pagina=1000):

    supabase = obtener_cliente_supabase()

    registros = []

    inicio = 0

    while True:

        fin = inicio + tamanio_pagina - 1

        respuesta = (
            supabase
            .table(tabla)
            .select("*")
            .eq("carga_id", carga_id)
            .range(inicio, fin)
            .execute()
        )

        pagina = respuesta.data

        if not pagina:
            break

        registros.extend(pagina)

        if len(pagina) < tamanio_pagina:
            break

        inicio += tamanio_pagina

    return registros


def construir_df_participaciones(registros_participaciones, jornada, carga):

    if not registros_participaciones:
        return pd.DataFrame()

    df = pd.DataFrame(registros_participaciones)

    columnas_a_renombrar = {
        columna_db: columna_display
        for columna_db, columna_display in COLUMNAS_PARTICIPACIONES_INVERSO.items()
        if columna_db in df.columns
    }

    df = df.rename(columns=columnas_a_renombrar)

    df = df.drop(columns=["id", "carga_id"], errors="ignore")

    df["anio"] = jornada["anio"]
    df["fecha_inicio_jornada"] = jornada["fecha_inicio"]
    df["fecha_fin_jornada"] = jornada["fecha_fin"]
    df["numero_carga"] = carga["numero_carga"]
    df["fecha_carga"] = carga["fecha_carga"]

    return df


def cargar_historico():

    supabase = obtener_cliente_supabase()

    respuesta_jornadas = (
        supabase
        .table("jornadas")
        .select("id, anio, fecha_inicio, fecha_fin")
        .order("anio")
        .execute()
    )

    jornadas = respuesta_jornadas.data

    if not jornadas:
        return pd.DataFrame()

    ultimas_cargas = obtener_ultima_carga_por_jornada()

    dataframes = []

    for jornada in jornadas:

        carga = ultimas_cargas.get(jornada["id"])

        if carga is None:
            continue

        registros_participaciones = cargar_registros(
            "participaciones",
            carga["id"]
        )

        df = construir_df_participaciones(
            registros_participaciones,
            jornada,
            carga
        )

        if df.empty:
            continue

        dataframes.append(df)

    if not dataframes:
        return pd.DataFrame()

    return pd.concat(dataframes, ignore_index=True)
