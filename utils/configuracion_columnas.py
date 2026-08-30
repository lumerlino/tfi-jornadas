from utils.supabase_cliente import obtener_cliente_supabase


def obtener_configuraciones():

    supabase = obtener_cliente_supabase()

    respuesta = (
        supabase
        .table("columnas_configuradas")
        .select("columna_excel, nombre_display, tipo_dato, metrica")
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
