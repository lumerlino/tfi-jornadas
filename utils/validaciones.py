COLUMNAS_OBLIGATORIAS = [
    "Nombre/s",
    "Apellido/s",
    "documento",
    "mail",
    "Miembro UNLa",
    "Rol principal",
    "Tipo inscripción",
    "Source",
    "IsWelcomeMailSent",
    "QRCode",
    "isPresent",
    "IsAssistanceCertifySent"
]


def validar_columnas(df):

    # Las columnas "Asistencia YYYY-MM-DD" son opcionales: si
    # existen, habilitan asistencia por día; si no (como en el
    # Excel 2024, que solo trae "isPresent"), utils/limpieza_datos.py
    # ::limpiar_datos ya sabe usar "isPresent" directo como fuente
    # de asistencia. No hace falta exigirlas acá.

    columnas_faltantes = [
        columna
        for columna in COLUMNAS_OBLIGATORIAS
        if columna not in df.columns
    ]

    return columnas_faltantes
