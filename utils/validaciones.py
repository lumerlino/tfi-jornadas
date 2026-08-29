from utils.limpieza_datos import detectar_columnas_asistencia


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

    columnas_faltantes = [
        columna
        for columna in COLUMNAS_OBLIGATORIAS
        if columna not in df.columns
    ]

    if not detectar_columnas_asistencia(df):

        columnas_faltantes.append(
            "Asistencia YYYY-MM-DD (al menos un día)"
        )

    return columnas_faltantes
