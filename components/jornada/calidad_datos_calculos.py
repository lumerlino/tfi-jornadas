from utils.calidad_datos import obtener_mascaras_calidad


def calcular_calidad_datos(df):
    total_registros = len(df)
    mascaras = obtener_mascaras_calidad(df)

    filas_duplicadas = df.duplicated().sum()

    documentos_faltantes = (
        (~mascaras["documento_valido"]).sum()
    )

    rol_informado = (
        df["Rol principal"].notna()
        & df["Rol principal"].astype(str).str.strip().ne("")
        & df["Rol principal"].astype(str).str.lower().ne("nan")
    )

    tipo_inscripcion_informado = (
        df["Tipo inscripción"].notna()
        & df["Tipo inscripción"].astype(str).str.strip().ne("")
        & df["Tipo inscripción"].astype(str).str.lower().ne("nan")
    )

    welcome_mail_enviado = (
        df["IsWelcomeMailSent"].mean() * 100
        if "IsWelcomeMailSent" in df.columns
        and df["IsWelcomeMailSent"].notna().any()
        else None
    )

    documentos_duplicados = (
        (~mascaras["documento_unico"]).sum()
    )

    participantes_unicos = df["documento"].nunique()

    reinscripciones = (
        total_registros - participantes_unicos
    )

    inscripciones_por_documento = (
        df["documento"].value_counts()
    )

    inscripciones_repetidas = (
        inscripciones_por_documento[
            inscripciones_por_documento > 1
        ]
    )

    participantes_reinscriptos = len(
        inscripciones_repetidas
    )

    distribucion_reinscripciones = (
        inscripciones_repetidas
        .value_counts()
        .sort_index()
    )

    mails_invalidos = (
        (~mascaras["mail_valido"]).sum()
    )

    inconsistencias_asistencia = (
        (~mascaras["asistencia_coherente"]).sum()
    )

    roles_faltantes = (~rol_informado).sum()

    tipos_inscripcion_faltantes = (
        (~tipo_inscripcion_informado).sum()
    )

    welcome_mail_no_enviado = (
        (~df["IsWelcomeMailSent"]).sum()
        if "IsWelcomeMailSent" in df.columns
        and df["IsWelcomeMailSent"].notna().any()
        else 0
    )

    problemas = (
        (~mascaras["documento_valido"])
        | (~mascaras["mail_valido"])
        | (~rol_informado)
        | (~tipo_inscripcion_informado)
        | (~mascaras["asistencia_coherente"])
    )

    registros_problematicos = problemas.sum()

    registros_sin_problemas = (
        total_registros - registros_problematicos
    )

    porcentaje_sin_problemas = (
        registros_sin_problemas / total_registros * 100
        if total_registros > 0
        else 0
    )

    return {
        "total_registros": total_registros,
        "mascaras": mascaras,
        "filas_duplicadas": filas_duplicadas,
        "documentos_faltantes": documentos_faltantes,
        "rol_informado": rol_informado,
        "tipo_inscripcion_informado": tipo_inscripcion_informado,
        "welcome_mail_enviado": welcome_mail_enviado,
        "documentos_duplicados": documentos_duplicados,
        "reinscripciones": reinscripciones,
        "participantes_reinscriptos": participantes_reinscriptos,
        "distribucion_reinscripciones": distribucion_reinscripciones,
        "mails_invalidos": mails_invalidos,
        "inconsistencias_asistencia": inconsistencias_asistencia,
        "roles_faltantes": roles_faltantes,
        "tipos_inscripcion_faltantes": tipos_inscripcion_faltantes,
        "welcome_mail_no_enviado": welcome_mail_no_enviado,
        "registros_problematicos": registros_problematicos,
        "porcentaje_sin_problemas": porcentaje_sin_problemas,
    }