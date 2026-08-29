def obtener_mascaras_calidad(df):

    documento_valido = (
        df["documento"].notna()
        & (df["documento"].astype(str).str.strip() != "")
        & (df["documento"].astype(str).str.strip() != "nan")
    )

    documento_unico = (
        ~df["documento"].duplicated(keep=False)
    )

    mail_valido = (
        df["mail"].notna()
        & df["mail"].astype(str).str.contains(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            regex=True,
            na=False
        )
    )

    columnas_obligatorias = [
        "Nombre/s",
        "Apellido/s",
        "documento",
        "mail",
        "Rol principal"
    ]

    datos_completos = (
        df[columnas_obligatorias]
        .notna()
        .all(axis=1)
    )

    asistencia_coherente = (
        df["isPresent_original"] == df["asistio"]
    )

    return {
        "documento_valido": documento_valido,
        "documento_unico": documento_unico,
        "mail_valido": mail_valido,
        "datos_completos": datos_completos,
        "asistencia_coherente": asistencia_coherente
    }
