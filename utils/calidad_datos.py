def obtener_mascaras_calidad(df):

    estados_qr_validos = [
        "Correcto",
        "Error"
    ]

    valido_participacion = (
        df["actividad"].notna()
        & df["fecha"].notna()
    )

    valido_persona_unica = (
        valido_participacion
        & df["id_participante"].notna()
    )

    valido_permanencia = (
        valido_participacion
        & df["hora_ingreso"].notna()
        & df["hora_egreso"].notna()
        & (df["hora_egreso"] >= df["hora_ingreso"])
    )

    valido_qr = (
        df["estado_qr"].isin(estados_qr_validos)
    )

    valido_ocupacion = (
        valido_participacion
        & df["capacidad_aula"].notna()
        & (df["capacidad_aula"] > 0)
    )

    return {
        "participacion": valido_participacion,
        "persona_unica": valido_persona_unica,
        "permanencia": valido_permanencia,
        "qr": valido_qr,
        "ocupacion": valido_ocupacion
    }