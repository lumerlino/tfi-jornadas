import pandas as pd

from utils.supabase_cliente import obtener_cliente_supabase


def validar_metadatos_jornada(metadatos):

    errores = []

    if metadatos["fecha_fin"] < metadatos["fecha_inicio"]:
        errores.append(
            "La fecha de fin no puede ser anterior a la fecha de inicio."
        )

    return errores


def obtener_o_crear_jornada(metadatos):

    supabase = obtener_cliente_supabase()

    anio = metadatos["anio"]

    respuesta = (
        supabase
        .table("jornadas")
        .select("*")
        .eq("anio", anio)
        .execute()
    )

    if respuesta.data:

        jornada = respuesta.data[0]

        respuesta_actualizacion = (
            supabase
            .table("jornadas")
            .update(
                {
                    "fecha_inicio": metadatos["fecha_inicio"].isoformat(),
                    "fecha_fin": metadatos["fecha_fin"].isoformat()
                }
            )
            .eq("id", jornada["id"])
            .execute()
        )

        if respuesta_actualizacion.data:
            jornada = respuesta_actualizacion.data[0]

        return jornada


    respuesta_creacion = (
        supabase
        .table("jornadas")
        .insert(
            {
                "anio": anio,
                "fecha_inicio": metadatos["fecha_inicio"].isoformat(),
                "fecha_fin": metadatos["fecha_fin"].isoformat()
            }
        )
        .execute()
    )

    return respuesta_creacion.data[0]


def obtener_proximo_numero_carga(jornada_id):

    supabase = obtener_cliente_supabase()

    respuesta = (
        supabase
        .table("cargas")
        .select("numero_carga")
        .eq("jornada_id", jornada_id)
        .order(
            "numero_carga",
            desc=True
        )
        .limit(1)
        .execute()
    )

    if not respuesta.data:
        return 1

    return (
        respuesta.data[0]["numero_carga"]
        + 1
    )


def crear_carga(jornada_id):

    supabase = obtener_cliente_supabase()

    numero_carga = (
        obtener_proximo_numero_carga(
            jornada_id
        )
    )

    respuesta = (
        supabase
        .table("cargas")
        .insert(
            {
                "jornada_id": jornada_id,
                "numero_carga": numero_carga
            }
        )
        .execute()
    )

    carga = respuesta.data[0]

    return carga


def preparar_valor(valor, columna):

    if pd.isna(valor):
        return None


    # Fecha
    if columna == "fecha":

        fecha = pd.to_datetime(
            valor,
            errors="coerce"
        )

        if pd.isna(fecha):
            return None

        return fecha.date().isoformat()


    # Horas
    columnas_hora = [
        "hora_inicio_actividad",
        "hora_fin_actividad",
        "hora_ingreso",
        "hora_egreso"
    ]

    if columna in columnas_hora:

        hora = pd.to_datetime(
            valor,
            errors="coerce"
        )

        if pd.isna(hora):
            return None

        return hora.strftime(
            "%H:%M:%S"
        )


    # Valores numéricos de NumPy
    if hasattr(valor, "item"):

        return valor.item()


    return valor

def preparar_participaciones(
    df,
    carga_id
):

    columnas = [
        "id_participante",
        "tipo_participante",
        "carrera",
        "institucion",
        "actividad",
        "tipo_actividad",
        "tematica",
        "aula",
        "capacidad_aula",
        "estado_qr",
        "punto_acceso",
        "fecha",
        "hora_inicio_actividad",
        "hora_fin_actividad",
        "hora_ingreso",
        "hora_egreso",
        "inscripto",
        "asistio"
    ]

    registros = []

    for _, fila in df.iterrows():

        registro = {
            "carga_id": carga_id
        }

        for columna in columnas:

            valor = fila.get(
                columna
            )

            valor = preparar_valor(
                valor,
                columna
            )

            registro[columna] = valor

        registros.append(
            registro
        )

    return registros


def guardar_participaciones(
    df,
    carga_id
):

    supabase = obtener_cliente_supabase()

    registros = preparar_participaciones(
        df,
        carga_id
    )

    tamanio_lote = 500

    for inicio in range(
        0,
        len(registros),
        tamanio_lote
    ):

        lote = registros[
            inicio:
            inicio + tamanio_lote
        ]

        (
            supabase
            .table("participaciones")
            .insert(lote)
            .execute()
        )


def guardar_carga(
    df,
    metadatos
):

    jornada = obtener_o_crear_jornada(
        metadatos
    )

    carga = crear_carga(
        jornada["id"]
    )

    try:

        guardar_participaciones(
            df,
            carga["id"]
        )

    except Exception:

        supabase = obtener_cliente_supabase()

        (
            supabase
            .table("cargas")
            .delete()
            .eq("id", carga["id"])
            .execute()
        )

        raise


    return {
        "guardado": True,
        "jornada_id": jornada["id"],
        "carga_id": carga["id"],
        "numero_carga": carga["numero_carga"]
    }