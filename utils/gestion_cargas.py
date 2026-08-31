from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from utils.supabase_cliente import obtener_cliente_supabase
from utils.guardado_historico import (
    COLUMNAS_PARTICIPACIONES,
    COLUMNAS_PARTICIPACIONES_INVERSO as COLUMNAS_DB_A_DISPLAY
)


def _contar_participaciones_por_carga(tamanio_pagina=1000):

    # Una sola pasada paginada sobre "carga_id" en vez de una
    # consulta de conteo por cada carga (N+1) — mismo patrón de
    # paginación que utils/historico_datos.py::cargar_registros.

    supabase = obtener_cliente_supabase()

    conteos = {}
    inicio = 0

    while True:

        fin = inicio + tamanio_pagina - 1

        respuesta = (
            supabase
            .table("participaciones")
            .select("carga_id")
            .range(inicio, fin)
            .execute()
        )

        pagina = respuesta.data

        if not pagina:
            break

        for fila in pagina:
            conteos[fila["carga_id"]] = (
                conteos.get(fila["carga_id"], 0) + 1
            )

        if len(pagina) < tamanio_pagina:
            break

        inicio += tamanio_pagina

    return conteos


@st.cache_data(ttl=600, show_spinner="Cargando listado de cargas...")
def listar_cargas():

    supabase = obtener_cliente_supabase()

    jornadas = (
        supabase
        .table("jornadas")
        .select("id, anio")
        .order("anio")
        .execute()
        .data
    )

    anio_por_jornada = {
        jornada["id"]: jornada["anio"]
        for jornada in jornadas
    }

    cargas = (
        supabase
        .table("cargas")
        .select("id, jornada_id, numero_carga, fecha_carga")
        .order("numero_carga")
        .execute()
        .data
    )

    conteos_por_carga = _contar_participaciones_por_carga()

    resultado = []

    for carga in cargas:

        resultado.append(
            {
                "carga_id": carga["id"],
                "anio": anio_por_jornada.get(carga["jornada_id"]),
                "numero_carga": carga["numero_carga"],
                "fecha_carga": carga["fecha_carga"],
                "cantidad_participaciones": conteos_por_carga.get(
                    carga["id"], 0
                )
            }
        )

    resultado.sort(
        key=lambda fila: (fila["anio"] or 0, fila["numero_carga"])
    )

    return resultado


def eliminar_carga(carga_id):

    supabase = obtener_cliente_supabase()

    # "cargas" tiene ON DELETE CASCADE hacia "participaciones" y
    # "asistencias_dia" (ver supabase/migrations/0001_esquema_historico.sql),
    # así que borrar la carga se lleva todo lo que dependía de ella.
    supabase.table("cargas").delete().eq("id", carga_id).execute()


def obtener_participaciones_carga(carga_id):

    supabase = obtener_cliente_supabase()

    respuesta = (
        supabase
        .table("participaciones")
        .select("*")
        .eq("carga_id", carga_id)
        .execute()
    )

    if not respuesta.data:
        return pd.DataFrame()

    df = pd.DataFrame(respuesta.data)

    df = df.rename(columns=COLUMNAS_DB_A_DISPLAY)

    columnas_a_mostrar = ["id"] + [
        columna
        for columna in COLUMNAS_PARTICIPACIONES.keys()
        if columna in df.columns
    ]

    return df[columnas_a_mostrar]


def actualizar_participacion(id_participacion, cambios_display):

    supabase = obtener_cliente_supabase()

    datos = {
        COLUMNAS_PARTICIPACIONES[columna_display]: valor
        for columna_display, valor in cambios_display.items()
        if columna_display in COLUMNAS_PARTICIPACIONES
    }

    datos["updated_at"] = datetime.now(timezone.utc).isoformat()

    supabase.table("participaciones").update(datos).eq(
        "id", id_participacion
    ).execute()
