COLUMNAS_OBLIGATORIAS = [
    "id_participante",
    "tipo_participante",
    "carrera",
    "institucion",
    "fecha",
    "actividad",
    "tipo_actividad",
    "tematica",
    "aula",
    "capacidad_aula",
    "hora_inicio_actividad",
    "hora_fin_actividad",
    "hora_ingreso",
    "hora_egreso",
    "inscripto",
    "asistio",
    "estado_qr",
    "punto_acceso"
]

def validar_columnas(df):

    columnas_faltantes = [
        columna
        for columna in COLUMNAS_OBLIGATORIAS
        if columna not in df.columns
    ]

    return columnas_faltantes