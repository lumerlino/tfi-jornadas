def calcular_objetivo(df_historico, anio_objetivo, asistentes_objetivo, tendencia):

    asistentes_por_anio = (
        df_historico
        .groupby("anio")["asistio"]
        .sum()
        .reset_index(name="asistentes")
        .sort_values("anio")
    )

    fila_actual = asistentes_por_anio.iloc[-1]

    anio_actual = int(fila_actual["anio"])
    asistentes_actuales = int(fila_actual["asistentes"])

    brecha = asistentes_objetivo - asistentes_actuales

    resultado = {
        "anio_actual": anio_actual,
        "asistentes_actuales": asistentes_actuales,
        "brecha": brecha,
        "tiene_tendencia": False
    }

    if not tendencia["suficiente"]:
        return resultado

    anios_restantes = anio_objetivo - anio_actual

    if anios_restantes <= 0 or asistentes_actuales <= 0:
        return resultado

    tasa_necesaria = (
        (asistentes_objetivo / asistentes_actuales)
        ** (1 / anios_restantes)
        - 1
    )

    fila_primera = asistentes_por_anio.iloc[0]

    anios_historicos = (
        int(fila_actual["anio"])
        - int(fila_primera["anio"])
    )

    if anios_historicos > 0 and fila_primera["asistentes"] > 0:

        tasa_historica = (
            (asistentes_actuales / fila_primera["asistentes"])
            ** (1 / anios_historicos)
            - 1
        )

    else:

        tasa_historica = None

    resultado["tiene_tendencia"] = True
    resultado["anios_restantes"] = anios_restantes
    resultado["tasa_necesaria"] = tasa_necesaria
    resultado["tasa_historica"] = tasa_historica

    return resultado
