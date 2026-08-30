from datetime import datetime, timezone

import pandas as pd

from utils.supabase_cliente import obtener_cliente_supabase
from utils.guardado_historico import COLUMNAS_PARTICIPACIONES


# Inverso de COLUMNAS_PARTICIPACIONES: de columna de la tabla
# (snake_case) al nombre "de display" que se usa en el editor.
COLUMNAS_DB_A_DISPLAY = {
    columna_db: columna_display
    for columna_display, columna_db in COLUMNAS_PARTICIPACIONES.items()
}


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

    resultado = []

    for carga in cargas:

        conteo = (
            supabase
            .table("participaciones")
            .select("id", count="exact")
            .eq("carga_id", carga["id"])
            .execute()
        )

        resultado.append(
            {
                "carga_id": carga["id"],
                "anio": anio_por_jornada.get(carga["jornada_id"]),
                "numero_carga": carga["numero_carga"],
                "fecha_carga": carga["fecha_carga"],
                "cantidad_participaciones": conteo.count or 0
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
