import pandas as pd

from utils.supabase_cliente import obtener_cliente_supabase


def obtener_ultima_carga_por_jornada():

    supabase = obtener_cliente_supabase()

    respuesta = (
        supabase
        .table("cargas")
        .select(
            "id, jornada_id, numero_carga, fecha_carga"
        )
        .order(
            "numero_carga",
            desc=True
        )
        .execute()
    )

    cargas = respuesta.data

    ultimas_cargas = {}

    for carga in cargas:

        jornada_id = carga["jornada_id"]

        if jornada_id not in ultimas_cargas:
            ultimas_cargas[jornada_id] = carga

    return ultimas_cargas


def cargar_participaciones_carga(
    carga_id,
    tamanio_pagina=1000
):

    supabase = obtener_cliente_supabase()

    registros = []

    inicio = 0

    while True:

        fin = (
            inicio
            + tamanio_pagina
            - 1
        )

        respuesta = (
            supabase
            .table("participaciones")
            .select("*")
            .eq(
                "carga_id",
                carga_id
            )
            .range(
                inicio,
                fin
            )
            .execute()
        )

        pagina = respuesta.data

        if not pagina:
            break

        registros.extend(
            pagina
        )

        if len(pagina) < tamanio_pagina:
            break

        inicio += tamanio_pagina

    return registros


def cargar_historico():

    supabase = obtener_cliente_supabase()

    # --------------------------------------------------
    # JORNADAS
    # --------------------------------------------------

    respuesta_jornadas = (
        supabase
        .table("jornadas")
        .select(
            "id, anio, fecha_inicio, fecha_fin"
        )
        .order(
            "anio"
        )
        .execute()
    )

    jornadas = respuesta_jornadas.data

    if not jornadas:
        return pd.DataFrame()


    # --------------------------------------------------
    # ÚLTIMA CARGA DE CADA JORNADA
    # --------------------------------------------------

    ultimas_cargas = (
        obtener_ultima_carga_por_jornada()
    )


    dataframes = []


    # --------------------------------------------------
    # PARTICIPACIONES
    # --------------------------------------------------

    for jornada in jornadas:

        jornada_id = jornada["id"]

        carga = ultimas_cargas.get(
            jornada_id
        )

        if carga is None:
            continue


        participaciones = (
            cargar_participaciones_carga(
                carga["id"]
            )
        )


        if not participaciones:
            continue


        df = pd.DataFrame(
            participaciones
        )


        # --------------------------------------------------
        # DATOS DE LA JORNADA
        # --------------------------------------------------

        df["anio"] = jornada[
            "anio"
        ]

        df["fecha_inicio_jornada"] = (
            jornada[
                "fecha_inicio"
            ]
        )

        df["fecha_fin_jornada"] = (
            jornada[
                "fecha_fin"
            ]
        )


        # --------------------------------------------------
        # DATOS DE LA CARGA
        # --------------------------------------------------

        df["numero_carga"] = carga[
            "numero_carga"
        ]

        df["fecha_carga"] = carga[
            "fecha_carga"
        ]


        dataframes.append(
            df
        )


    if not dataframes:
        return pd.DataFrame()


    df_historico = pd.concat(
        dataframes,
        ignore_index=True
    )


    return df_historico