from utils.supabase_cliente import obtener_cliente_supabase


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
