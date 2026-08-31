import pandas as pd

from utils.supabase_cliente import obtener_cliente_supabase
from utils.limpieza_datos import (
    detectar_columnas_asistencia,
    construir_asistencia_larga
)
from utils.clasificacion_columnas import columnas_no_mapeadas


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


def preparar_valor(valor):

    if pd.isna(valor):
        return None

    # Valores numéricos/booleanos de NumPy
    if hasattr(valor, "item"):
        return valor.item()

    return valor


# --------------------------------------------------
# Columna del DataFrame limpio -> columna de la tabla
# "participaciones" en Supabase (snake_case)
# --------------------------------------------------

COLUMNAS_PARTICIPACIONES = {
    "Nombre/s": "nombre",
    "Apellido/s": "apellido",
    "documento": "documento",
    "mail": "mail",
    "Miembro UNLa": "miembro_unla",
    "Rol principal": "rol_principal",
    "Otro Rol principal": "otro_rol_principal",
    "Investigador Carreras": "investigador_carreras",
    "Otro Investigador Carreras": "otro_investigador_carreras",
    "Tipo inscripción": "tipo_inscripcion",
    "Source": "source",
    "IsWelcomeMailSent": "is_welcome_mail_sent",
    "QRCode": "qr_code",
    "isPresent_original": "is_present_original",
    "IsAssistanceCertifySent": "is_assistance_certify_sent",
    "asistio": "asistio"
}


# Inverso de lo anterior: de columna de la tabla (snake_case) al
# nombre "de display" que usan los componentes de jornada/histórico
# (ej. "rol_principal" -> "Rol principal"). Única fuente de verdad
# para este mapeo — utils/historico_datos.py, utils/gestion_cargas.py
# y utils/jornada_guardada.py lo importan de acá.
COLUMNAS_PARTICIPACIONES_INVERSO = {
    columna_destino: columna_origen
    for columna_origen, columna_destino in COLUMNAS_PARTICIPACIONES.items()
}


def preparar_participaciones(df, carga_id):

    columnas_extra = columnas_no_mapeadas(
        df,
        COLUMNAS_PARTICIPACIONES.keys()
    )

    registros = []

    for _, fila in df.iterrows():

        registro = {
            "carga_id": carga_id
        }

        for columna_origen, columna_destino in COLUMNAS_PARTICIPACIONES.items():

            valor = fila.get(columna_origen)

            registro[columna_destino] = preparar_valor(valor)

        # Columnas del Excel que todavía no tienen una columna
        # propia en la tabla (ej. un campo nuevo agregado al
        # formulario de inscripción) no se pierden: quedan acá
        # hasta que se decida "promoverlas" a columna real.
        if columnas_extra:

            registro["datos_extra"] = {
                columna: preparar_valor(fila.get(columna))
                for columna in columnas_extra
            }

        registros.append(registro)

    return registros


def preparar_asistencias_dia(df, carga_id, id_por_documento=None):

    columnas_asistencia = detectar_columnas_asistencia(df)

    if not columnas_asistencia:
        return []

    asistencia_larga = construir_asistencia_larga(
        df,
        columnas_asistencia
    )

    id_por_documento = id_por_documento or {}

    registros = []

    for _, fila in asistencia_larga.iterrows():

        documento = preparar_valor(fila["documento"])

        registros.append(
            {
                "carga_id": carga_id,
                "documento": documento,
                # Enlace real por id (ver migración 0003) en vez
                # de depender solo del texto de "documento", que
                # se rompería silenciosamente si algún día se edita.
                "participacion_id": id_por_documento.get(documento),
                "fecha": fila["fecha"].date().isoformat(),
                "asistio": bool(fila["asistio"])
            }
        )

    return registros


def guardar_en_lotes(tabla, registros, tamanio_lote=500):

    if not registros:
        return []

    supabase = obtener_cliente_supabase()

    insertados = []

    for inicio in range(0, len(registros), tamanio_lote):

        lote = registros[inicio:inicio + tamanio_lote]

        respuesta = supabase.table(tabla).insert(lote).execute()

        insertados.extend(respuesta.data)

    return insertados


def guardar_carga(df, metadatos):

    jornada = obtener_o_crear_jornada(metadatos)

    carga = crear_carga(jornada["id"])

    try:

        participaciones = preparar_participaciones(df, carga["id"])

        participaciones_guardadas = guardar_en_lotes(
            "participaciones",
            participaciones
        )

        id_por_documento = {
            fila["documento"]: fila["id"]
            for fila in participaciones_guardadas
            if fila.get("documento") is not None
        }

        asistencias_dia = preparar_asistencias_dia(
            df,
            carga["id"],
            id_por_documento
        )

        guardar_en_lotes("asistencias_dia", asistencias_dia)

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
