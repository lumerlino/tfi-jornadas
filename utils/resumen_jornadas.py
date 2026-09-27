import pandas as pd

from utils.proyecciones import calcular_tendencia


# --------------------------------------------------
# CÁLCULOS DE "CÓMO NOS FUE"
#
# Todo se cuenta en personas (documentos únicos), no en filas:
#   inscriptos -> documentos distintos de la edición
#   vinieron   -> documentos distintos con asistio == True
# Son funciones de pandas puras (sin Streamlit) para poder
# probarlas sin la base de datos.
# --------------------------------------------------


# Cambios de un grupo por debajo de esto se consideran ruido y no
# generan hallazgo (una o dos personas no son una tendencia).
CAMBIO_MINIMO_GRUPO = 5


def formatear_numero(numero):

    return f"{int(numero):,}".replace(",", ".")


def personas(numero):

    numero = int(numero)

    return f"{formatear_numero(numero)} persona{'' if numero == 1 else 's'}"


def resumen_anual(df_historico):

    personas = df_historico.dropna(subset=["documento"])

    inscriptos = personas.groupby("anio")["documento"].nunique()

    vinieron = (
        personas[personas["asistio"].astype(bool)]
        .groupby("anio")["documento"]
        .nunique()
    )

    resumen = pd.DataFrame({
        "inscriptos": inscriptos,
        "vinieron": vinieron
    }).fillna(0).astype(int)

    resumen.index.name = "anio"

    return resumen.reset_index().sort_values("anio")


def de_cada_10(vinieron, inscriptos):

    if inscriptos <= 0:
        return 0

    return round(vinieron / inscriptos * 10)


def variacion_porcentual(actual, anterior):

    if anterior <= 0:
        return None

    return (actual - anterior) / anterior * 100


def volvieron(df_historico, anio_anterior, anio):

    asistentes = df_historico[df_historico["asistio"].astype(bool)]

    documentos_anterior = set(
        asistentes[asistentes["anio"] == anio_anterior]["documento"].dropna()
    )

    documentos_actual = set(
        asistentes[asistentes["anio"] == anio]["documento"].dropna()
    )

    cantidad = len(documentos_anterior & documentos_actual)

    porcentaje = (
        cantidad / len(documentos_anterior) * 100
        if documentos_anterior
        else 0
    )

    return cantidad, porcentaje


def cambios_por_grupo(df_historico, anio_anterior, anio, columna="Rol principal"):

    asistentes = df_historico[
        df_historico["asistio"].astype(bool)
        & df_historico["anio"].isin([anio_anterior, anio])
    ].dropna(subset=["documento", columna])

    tabla = (
        asistentes
        .groupby([columna, "anio"])["documento"]
        .nunique()
        .unstack(fill_value=0)
        .reindex(columns=[anio_anterior, anio], fill_value=0)
    )

    tabla["diferencia"] = tabla[anio] - tabla[anio_anterior]

    return tabla.sort_values("diferencia")


# --------------------------------------------------
# HALLAZGOS: frases generadas por reglas simples.
# Cada uno es {"tipo": bajo|subio|atencion|igual, "texto": ...}
# --------------------------------------------------


def _hallazgo_asistencia(fila, fila_anterior):

    anio_anterior = int(fila_anterior["anio"])

    vinieron = int(fila["vinieron"])
    vinieron_antes = int(fila_anterior["vinieron"])

    inscriptos = int(fila["inscriptos"])
    inscriptos_antes = int(fila_anterior["inscriptos"])

    variacion = variacion_porcentual(vinieron, vinieron_antes)

    if variacion is None or abs(variacion) < 2:

        return {
            "tipo": "igual",
            "texto": (
                f"Vinieron {personas(vinieron)}, casi las "
                f"mismas que en {anio_anterior} "
                f"({formatear_numero(vinieron_antes)})."
            )
        }

    if variacion > 0:

        return {
            "tipo": "subio",
            "texto": (
                f"Vinieron {personas(vinieron)}, "
                f"{abs(variacion):.0f} % más que en {anio_anterior}."
            )
        }

    texto = (
        f"Vinieron {personas(vinieron)}, "
        f"{abs(variacion):.0f} % menos que en {anio_anterior}"
    )

    variacion_inscriptos = variacion_porcentual(inscriptos, inscriptos_antes)

    if variacion_inscriptos is None or abs(variacion_inscriptos) < 5:
        texto += ", aunque se anotó casi la misma cantidad."
    elif variacion_inscriptos < 0:
        texto += (
            f", y también se anotaron menos personas "
            f"({formatear_numero(inscriptos)} contra "
            f"{formatear_numero(inscriptos_antes)})."
        )
    else:
        texto += (
            f", aunque se anotaron más personas "
            f"({formatear_numero(inscriptos)} contra "
            f"{formatear_numero(inscriptos_antes)})."
        )

    return {"tipo": "bajo", "texto": texto}


def _hallazgo_grupos(df_historico, anio_anterior, anio):

    cambios = cambios_por_grupo(df_historico, anio_anterior, anio)

    if cambios.empty:
        return None

    mayor_caida = cambios.iloc[0]
    mayor_suba = cambios.iloc[-1]

    grupo_caida = cambios.index[0]
    grupo_suba = cambios.index[-1]

    bajo = mayor_caida["diferencia"] <= -CAMBIO_MINIMO_GRUPO
    subio = mayor_suba["diferencia"] >= CAMBIO_MINIMO_GRUPO

    if bajo:

        texto = (
            f"El grupo que más bajó fue {grupo_caida}: vinieron "
            f"{personas(-mayor_caida['diferencia'])} menos que en "
            f"{anio_anterior}."
        )

        if subio:
            texto += (
                f" En cambio, {grupo_suba} creció "
                f"({formatear_numero(mayor_suba['diferencia'])} más)."
            )

        return {"tipo": "bajo", "texto": texto}

    if subio:

        return {
            "tipo": "subio",
            "texto": (
                f"Ningún grupo bajó. El que más creció fue {grupo_suba} "
                f"({personas(mayor_suba['diferencia'])} más que en "
                f"{anio_anterior})."
            )
        }

    return {
        "tipo": "igual",
        "texto": (
            f"Todos los grupos tuvieron una asistencia parecida a la de "
            f"{anio_anterior}."
        )
    }


def _hallazgo_tendencia(resumen_hasta_anio):

    anio = int(resumen_hasta_anio["anio"].iloc[-1])
    vinieron = int(resumen_hasta_anio["vinieron"].iloc[-1])

    # calcular_tendencia suma "asistio" por año: con una fila por año
    # y asistio = vinieron, la serie es la de personas.
    tendencia = calcular_tendencia(
        resumen_hasta_anio.rename(columns={"vinieron": "asistio"})[["anio", "asistio"]]
    )

    if not tendencia["suficiente"]:

        faltan = tendencia["anios_necesarios"] - tendencia["anios_disponibles"]

        return {
            "tipo": "atencion",
            "texto": (
                "Todavía no se puede estimar una tendencia: "
                + (
                    "hace falta 1 edición más"
                    if faltan == 1
                    else f"hacen falta {faltan} ediciones más"
                )
                + " en el histórico."
            )
        }

    proyeccion = int(round(tendencia["proyeccion"] / 10) * 10)
    proximo = tendencia["proximo_anio"]

    serie = resumen_hasta_anio["vinieron"].tolist()
    bajo_dos_veces = len(serie) >= 3 and serie[-1] < serie[-2] < serie[-3]

    if proyeccion > vinieron:

        texto = (
            f"Si seguimos la tendencia, en {proximo} vendrían unas "
            f"{formatear_numero(proyeccion)} personas y superaríamos {anio}."
        )

        if bajo_dos_veces:
            return {
                "tipo": "atencion",
                "texto": texto + " Pero bajamos dos años seguidos, así que no está asegurado."
            }

        return {"tipo": "subio", "texto": texto}

    return {
        "tipo": "bajo",
        "texto": (
            f"Si seguimos como hasta ahora, en {proximo} vendrían unas "
            f"{formatear_numero(proyeccion)} personas: no alcanzaría para "
            f"superar {anio}."
        )
    }


def hallazgos(df_historico, anio):

    resumen = resumen_anual(df_historico)
    resumen = resumen[resumen["anio"] <= anio]

    if len(resumen) < 2:
        return []

    fila = resumen.iloc[-1]
    fila_anterior = resumen.iloc[-2]

    resultado = [
        _hallazgo_asistencia(fila, fila_anterior),
        _hallazgo_grupos(df_historico, int(fila_anterior["anio"]), anio),
        _hallazgo_tendencia(resumen),
    ]

    return [h for h in resultado if h is not None]
