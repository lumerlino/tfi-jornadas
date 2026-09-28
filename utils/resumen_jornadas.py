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


# --------------------------------------------------
# "QUÉ CAMBIÓ"
# --------------------------------------------------


def titular_cambios(df_historico, anio_anterior, anio):

    cambios = cambios_por_grupo(df_historico, anio_anterior, anio)

    if cambios.empty:
        return f"No hay datos de rol para comparar con {anio_anterior}."

    caida = cambios.iloc[0]
    suba = cambios.iloc[-1]

    grupo_caida = cambios.index[0]
    grupo_suba = cambios.index[-1]

    bajo = caida["diferencia"] <= -CAMBIO_MINIMO_GRUPO
    subio = suba["diferencia"] >= CAMBIO_MINIMO_GRUPO

    if bajo and subio:
        return (
            f"Frente a {anio_anterior}, vinieron {personas(-caida['diferencia'])} "
            f"menos del grupo {grupo_caida} y "
            f"{formatear_numero(suba['diferencia'])} más de {grupo_suba}."
        )

    if bajo:
        return (
            f"Frente a {anio_anterior}, el grupo que más bajó fue "
            f"{grupo_caida} ({personas(-caida['diferencia'])} menos)."
        )

    if subio:
        return (
            f"Frente a {anio_anterior}, ningún grupo bajó; el que más creció "
            f"fue {grupo_suba} ({personas(suba['diferencia'])} más)."
        )

    return (
        f"Frente a {anio_anterior}, todos los grupos vinieron en cantidades "
        f"parecidas."
    )


def accion_sugerida(df_historico, anio_anterior, anio):

    cambios = cambios_por_grupo(df_historico, anio_anterior, anio)

    if cambios.empty:
        return None

    if cambios.iloc[0]["diferencia"] <= -CAMBIO_MINIMO_GRUPO:
        return (
            f"Podemos reforzar la convocatoria al grupo {cambios.index[0]} "
            f"para la próxima jornada."
        )

    if cambios.iloc[-1]["diferencia"] >= CAMBIO_MINIMO_GRUPO:
        return (
            f"Lo que hicimos con el grupo {cambios.index[-1]} funcionó: "
            f"conviene repetirlo."
        )

    return None


# Carrera: la completan personas vinculadas a investigación, de
# cualquier rol. Es de opción múltiple: una misma celda puede traer
# varias carreras separadas por coma ("Lic. en Sistemas, Lic. en
# Logística" o sin espacio). Se separan antes de contar, así cada
# persona suma en cada carrera que indicó. "Otro" + texto libre se
# agrupa en "Otras áreas" (suelen ser áreas o secretarías).
COLUMNA_CARRERA = "Investigador Carreras"
OTRAS_AREAS = "Otras áreas"
VALORES_VACIOS = {"", "-", "nan", "none", "<na>"}


def _con_carreras(df):

    # Devuelve una fila por persona y carrera, en la columna
    # "carrera" (vacía si la persona no indicó ninguna).

    df = df.copy()

    listas = (
        df[COLUMNA_CARRERA]
        .astype("string")
        .fillna("")
        .str.split(",")
    )

    def limpiar(carreras):
        limpias = []
        for carrera in carreras:
            carrera = carrera.strip()
            if carrera.lower() in VALORES_VACIOS:
                continue
            if carrera.lower() == "otro":
                carrera = OTRAS_AREAS
            if carrera not in limpias:
                limpias.append(carrera)
        return limpias or [None]

    df["carrera"] = listas.apply(limpiar)

    return df.explode("carrera")


def roles_con_carrera(df_historico, anio):

    if COLUMNA_CARRERA not in df_historico.columns:
        return []

    asistentes = _con_carreras(df_historico[
        df_historico["asistio"].astype(bool)
        & (df_historico["anio"] == anio)
    ])

    conteo = (
        asistentes.dropna(subset=["carrera", "Rol principal"])
        .groupby("Rol principal")["documento"]
        .nunique()
        .sort_values(ascending=False)
    )

    return conteo.index.tolist()


def carreras_por_rol(df_historico, anio_anterior, anio, rol):

    # Devuelve (tabla por carrera, personas del grupo en el año,
    # personas sin carrera, personas con más de una carrera).

    asistentes = _con_carreras(df_historico[
        df_historico["asistio"].astype(bool)
        & df_historico["anio"].isin([anio_anterior, anio])
        & (df_historico["Rol principal"] == rol)
    ].dropna(subset=["documento"]))

    del_anio = asistentes[asistentes["anio"] == anio]

    total = del_anio["documento"].nunique()

    carreras_por_persona = (
        del_anio.dropna(subset=["carrera"])
        .groupby("documento")["carrera"]
        .nunique()
    )

    # Sin carrera = personas del año que no indicaron ninguna (si una
    # persona se inscribió dos veces y en una puso carrera, cuenta
    # como con carrera).
    sin_carrera = total - len(carreras_por_persona)
    varias_carreras = int((carreras_por_persona > 1).sum())

    tabla = (
        asistentes.dropna(subset=["carrera"])
        .groupby(["carrera", "anio"])["documento"]
        .nunique()
        .unstack(fill_value=0)
        .reindex(columns=[anio_anterior, anio], fill_value=0)
    )

    tabla = tabla[tabla[anio] > 0].copy()

    tabla["diferencia"] = tabla[anio] - tabla[anio_anterior]

    return (
        tabla.sort_values(anio, ascending=False),
        total,
        sin_carrera,
        varias_carreras
    )


def titular_carreras(tabla, total, sin_carrera, rol, anio_anterior, cambio_minimo=3):

    if tabla.empty:
        return f"Nadie del grupo {rol} indicó carrera."

    anio = tabla.columns[1]

    principal = tabla.index[0]
    cantidad_principal = formatear_numero(tabla.iloc[0][anio])

    if sin_carrera > 0:
        texto = (
            f"De las {personas(total)} del grupo {rol} que vinieron, "
            f"{formatear_numero(total - sin_carrera)} indicaron carrera; la "
            f"más frecuente es {principal} ({cantidad_principal})."
        )
    else:
        texto = (
            f"De las {personas(total)} del grupo {rol} que vinieron, la "
            f"carrera más frecuente es {principal} ({cantidad_principal})."
        )

    caida = tabla.sort_values("diferencia").iloc[0]

    if caida["diferencia"] <= -cambio_minimo:
        texto += (
            f" La que más bajó fue {caida.name} "
            f"({formatear_numero(-caida['diferencia'])} menos que en "
            f"{anio_anterior})."
        )

    return texto


def reencuentro(df_historico, anio_anterior, anio):

    resumen = resumen_anual(df_historico).set_index("anio")

    vinieron_antes = int(resumen.loc[anio_anterior, "vinieron"])
    vinieron = int(resumen.loc[anio, "vinieron"])

    cantidad, porcentaje = volvieron(df_historico, anio_anterior, anio)

    return (
        f"De las {personas(vinieron_antes)} que vinieron en {anio_anterior}, "
        f"{formatear_numero(cantidad)} volvieron en {anio} "
        f"({porcentaje:.0f} %). Las otras {personas(vinieron - cantidad)} de "
        f"{anio} no habían venido en {anio_anterior}."
    )


# --------------------------------------------------
# "NUESTRA PRÓXIMA JORNADA"
# --------------------------------------------------


def estimacion(resumen):

    # Misma regresión que el resto de la app (utils/proyecciones.py),
    # sobre las personas que vinieron cada año.
    return calcular_tendencia(
        resumen.rename(columns={"vinieron": "asistio"})[["anio", "asistio"]]
    )


def redondear_a_10(numero):

    return int(round(numero / 10) * 10)


def titular_meta(tendencia, meta, anio, vinieron):

    if not tendencia["suficiente"]:

        faltan = tendencia["anios_necesarios"] - tendencia["anios_disponibles"]

        return (
            "Todavía no hay suficientes ediciones para estimar hacia dónde "
            f"vamos (falta{'' if faltan == 1 else 'n'} {faltan}). Para "
            f"superar {anio} necesitamos más de {personas(vinieron)}."
        )

    proyeccion = redondear_a_10(tendencia["proyeccion"])
    diferencia = proyeccion - meta

    if diferencia > 0:
        return (
            f"Si seguimos como hasta ahora, vendrían unas "
            f"{formatear_numero(proyeccion)} personas: superaríamos la meta "
            f"por {formatear_numero(diferencia)}."
        )

    if diferencia == 0:
        return (
            f"Si seguimos como hasta ahora, vendrían unas "
            f"{formatear_numero(proyeccion)} personas: justo la meta, sin "
            f"margen."
        )

    return (
        f"Si seguimos como hasta ahora, vendrían unas "
        f"{formatear_numero(proyeccion)} personas: nos quedaríamos "
        f"{formatear_numero(-diferencia)} abajo de la meta."
    )


def aprendizajes(df_historico):

    resumen = resumen_anual(df_historico)

    if len(resumen) < 2:
        return []

    ultima = resumen.iloc[-1]
    anio = int(ultima["anio"])

    resultado = []

    # 1. La mejor jornada y qué grupo venía más ese año
    mejor = resumen.loc[resumen["vinieron"].idxmax()]
    anio_mejor = int(mejor["anio"])

    if anio_mejor == anio:

        resultado.append(
            f"{anio} fue nuestra mejor jornada hasta ahora, con "
            f"{personas(ultima['vinieron'])}."
        )

    else:

        texto = (
            f"Nuestra mejor jornada fue {anio_mejor} "
            f"({personas(mejor['vinieron'])})."
        )

        cambios = cambios_por_grupo(df_historico, anio_mejor, anio)

        if not cambios.empty and cambios.iloc[0]["diferencia"] <= -CAMBIO_MINIMO_GRUPO:
            texto += (
                f" Ese año vinieron {personas(-cambios.iloc[0]['diferencia'])} "
                f"más del grupo {cambios.index[0]} que en {anio}."
            )

        resultado.append(texto)

    # 2. Grupos que crecieron en todas las ediciones
    if len(resumen) >= 3:

        asistentes = df_historico[df_historico["asistio"].astype(bool)]

        por_grupo = (
            asistentes.dropna(subset=["documento", "Rol principal"])
            .groupby(["Rol principal", "anio"])["documento"]
            .nunique()
            .unstack(fill_value=0)
            .reindex(columns=resumen["anio"].tolist(), fill_value=0)
        )

        crecientes = [
            grupo
            for grupo, fila in por_grupo.iterrows()
            if fila.iloc[0] > 0 and fila.diff().iloc[1:].gt(0).all()
        ]

        if crecientes:
            resultado.append(
                f"El grupo {crecientes[0]} creció en todas las ediciones: lo "
                f"que hacemos con ese grupo funciona."
            )

    # 3. La proporción de inscriptos que viene
    proporciones = resumen["vinieron"] / resumen["inscriptos"].where(resumen["inscriptos"] > 0)

    mejor_proporcion = proporciones.idxmax()
    fila_proporcion = resumen.loc[mejor_proporcion]

    # Se compara lo que la persona ve ("6 de cada 10"), no la tasa
    # exacta: si redondeadas son iguales, la frase se contradiría.
    de_10_mejor = de_cada_10(fila_proporcion["vinieron"], fila_proporcion["inscriptos"])
    de_10_ultima = de_cada_10(ultima["vinieron"], ultima["inscriptos"])

    if de_10_mejor > de_10_ultima:

        estimados = redondear_a_10(ultima["inscriptos"] * proporciones[mejor_proporcion])

        resultado.append(
            f"En {int(fila_proporcion['anio'])} venían {de_10_mejor} de cada "
            f"10 inscriptos; en {anio}, {de_10_ultima}. Si "
            f"recuperamos eso, con la misma cantidad de inscriptos vendrían "
            f"unas {formatear_numero(estimados)} personas."
        )

    return resultado
