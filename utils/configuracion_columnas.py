import pandas as pd

from utils.supabase_cliente import obtener_cliente_supabase


# --------------------------------------------------
# Fallback si no hay conexión a Supabase: mismos valores
# que el seed de supabase/migrations/0002_columnas_configuradas.sql.
# Si alguien editó su configuración desde ⚙️ Configuración, ese
# cambio vive solo en la base — sin conexión se usa este default
# fijo, no la personalización.
# --------------------------------------------------

CONFIGURACION_POR_DEFECTO = {
    "Rol principal": {
        "nombre_display": "Rol principal",
        "tipo_dato": "categorica",
        "metrica": "Barras"
    },
    "Miembro UNLa": {
        "nombre_display": "Miembro UNLa",
        "tipo_dato": "booleana",
        "metrica": "Tasa (%)"
    },
    "Tipo inscripción": {
        "nombre_display": "Tipo de inscripción",
        "tipo_dato": "categorica",
        "metrica": "Barras"
    },
    "Source": {
        "nombre_display": "Origen de inscripción",
        "tipo_dato": "categorica",
        "metrica": "Barras"
    }
}


def obtener_configuraciones():

    supabase = obtener_cliente_supabase()

    respuesta = (
        supabase
        .table("columnas_configuradas")
        .select("columna_excel, nombre_display, tipo_dato, metrica")
        .order("creado_en")
        .execute()
    )

    return {
        fila["columna_excel"]: {
            "nombre_display": fila["nombre_display"],
            "tipo_dato": fila["tipo_dato"],
            "metrica": fila["metrica"]
        }
        for fila in respuesta.data
    }


def guardar_configuracion(columna_excel, nombre_display, tipo_dato, metrica):

    supabase = obtener_cliente_supabase()

    respuesta = (
        supabase
        .table("columnas_configuradas")
        .select("id")
        .eq("columna_excel", columna_excel)
        .execute()
    )

    datos = {
        "columna_excel": columna_excel,
        "nombre_display": nombre_display,
        "tipo_dato": tipo_dato,
        "metrica": metrica
    }

    if respuesta.data:

        supabase.table("columnas_configuradas").update(datos).eq(
            "columna_excel", columna_excel
        ).execute()

    else:

        supabase.table("columnas_configuradas").insert(datos).execute()


def eliminar_configuracion(columna_excel):

    supabase = obtener_cliente_supabase()

    supabase.table("columnas_configuradas").delete().eq(
        "columna_excel", columna_excel
    ).execute()


def obtener_valores_columna(columna_excel):

    supabase = obtener_cliente_supabase()

    respuesta = (
        supabase
        .table("participaciones")
        .select("datos_extra")
        .execute()
    )

    valores = []

    for fila in respuesta.data:

        extra = fila.get("datos_extra") or {}

        valores.append(extra.get(columna_excel))

    return pd.Series(valores, name=columna_excel)
