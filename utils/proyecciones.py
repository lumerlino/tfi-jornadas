import numpy as np


ANIOS_MINIMOS = 3


def calcular_tendencia(df_historico):

    asistentes_por_anio = (
        df_historico
        .groupby("anio")["asistio"]
        .sum()
        .reset_index(name="asistentes")
        .sort_values("anio")
    )

    anios_disponibles = len(asistentes_por_anio)

    if anios_disponibles < ANIOS_MINIMOS:

        return {
            "suficiente": False,
            "anios_disponibles": anios_disponibles,
            "anios_necesarios": ANIOS_MINIMOS,
            "serie": asistentes_por_anio
        }

    anios = asistentes_por_anio["anio"].to_numpy(dtype=float)
    asistentes = asistentes_por_anio["asistentes"].to_numpy(dtype=float)

    pendiente, ordenada = np.polyfit(anios, asistentes, 1)

    predicciones = pendiente * anios + ordenada

    total_varianza = np.sum((asistentes - asistentes.mean()) ** 2)

    if total_varianza == 0:
        r2 = 0.0
    else:
        residuos = np.sum((asistentes - predicciones) ** 2)
        r2 = 1 - (residuos / total_varianza)

    proximo_anio = int(anios.max()) + 1

    proyeccion = pendiente * proximo_anio + ordenada

    return {
        "suficiente": True,
        "anios_disponibles": anios_disponibles,
        "serie": asistentes_por_anio,
        "pendiente": pendiente,
        "ordenada": ordenada,
        "r2": r2,
        "proximo_anio": proximo_anio,
        "proyeccion": max(0, proyeccion)
    }
