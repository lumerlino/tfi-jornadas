import pandas as pd

from utils.limpieza_datos import PATRON_ASISTENCIA
from utils.resumen_jornadas import formatear_numero


# --------------------------------------------------
# DE DÓNDE SALE CADA NÚMERO
#
# Catálogo único para explicar las métricas: la ayuda corta de cada
# indicador (ícono "?"), la tabla "¿De dónde salen estos números?" y
# el paso a paso de "Vinieron". Así las tres explicaciones nunca se
# contradicen.
#
# La fuente de la asistencia depende de la edición: si el Excel trae
# columnas "Asistencia AAAA-MM-DD", asistió quien tiene al menos un
# "Si"; si no, se usa "isPresent" (ver utils/limpieza_datos.py). En
# 2025, por ejemplo, "isPresent" es falso para todos y se usan los
# días. Por eso la explicación se arma para cada edición.
# --------------------------------------------------


def codigo(nombre):

    return f"`{nombre}`"


def fuente_asistencia(df_anio):

    # Devuelve {"tipo": "dias" | "isPresent" | "registrada",
    #           "columnas": [...], "texto": "..."} para una edición.

    columnas_dias = [
        columna
        for columna in df_anio.columns
        if PATRON_ASISTENCIA.match(str(columna))
        and df_anio[columna].notna().any()
    ]

    if columnas_dias:
        return {
            "tipo": "dias",
            "columnas": sorted(columnas_dias),
            "texto": (
                "al menos un «Si» en "
                + ", ".join(codigo(c) for c in sorted(columnas_dias))
            ),
        }

    # Histórico guardado: los días están en otra tabla, pero se puede
    # saber qué se usó comparando el resultado con isPresent.
    if "isPresent_original" in df_anio.columns and "asistio" in df_anio.columns:

        difiere = (
            df_anio["asistio"].astype(bool)
            != df_anio["isPresent_original"].fillna(False).astype(bool)
        ).any()

        if difiere:

            rango = ""
            if "fecha_inicio_jornada" in df_anio.columns:
                inicio = pd.to_datetime(df_anio["fecha_inicio_jornada"].iloc[0])
                fin = pd.to_datetime(df_anio["fecha_fin_jornada"].iloc[0])
                rango = f" (del {inicio:%d/%m/%Y} al {fin:%d/%m/%Y})"

            return {
                "tipo": "dias",
                "columnas": [],
                "texto": f"al menos un «Si» en las columnas {codigo('Asistencia AAAA-MM-DD')}{rango}",
            }

        return {
            "tipo": "isPresent",
            "columnas": ["isPresent"],
            "texto": f"{codigo('isPresent')} en verdadero (el Excel no trae asistencia por día)",
        }

    return {
        "tipo": "registrada",
        "columnas": [],
        "texto": "asistencia registrada",
    }


# --------------------------------------------------
# A. AYUDA CORTA (ícono "?" de cada indicador)
# --------------------------------------------------


def ayuda(clave, fuente=None, anio_anterior=None):

    textos = {
        "se_anotaron": (
            f"Personas distintas de la edición, contadas por la columna "
            f"{codigo('documento')}. Si alguien se inscribió dos veces, cuenta una."
        ),
        "vinieron": (
            f"Personas distintas ({codigo('documento')}) con "
            + (fuente["texto"] if fuente else "asistencia registrada")
            + "."
        ),
        "de_cada_10": (
            "Vinieron ÷ se anotaron, llevado a «de cada 10» y redondeado."
        ),
        "volvieron": (
            f"Personas ({codigo('documento')}) que vinieron a {anio_anterior} "
            "y también a esta edición."
            if anio_anterior
            else f"Personas ({codigo('documento')}) que vinieron a las dos ediciones."
        ),
    }

    return textos[clave]


# --------------------------------------------------
# B. TABLA "¿DE DÓNDE SALEN ESTOS NÚMEROS?"
# Filas: (número, columnas del Excel, cálculo)
# --------------------------------------------------


def tabla_como_nos_fue(fuente, anio, anio_anterior):

    columnas_asistencia = (
        ", ".join(codigo(c) for c in fuente["columnas"])
        if fuente["columnas"]
        else codigo("Asistencia AAAA-MM-DD") if fuente["tipo"] == "dias"
        else codigo("isPresent") if fuente["tipo"] == "isPresent"
        else "—"
    )

    filas = [
        ("Se anotaron", codigo("documento"), "Documentos distintos de la edición."),
        (
            "Vinieron",
            f"{codigo('documento')} + {columnas_asistencia}",
            "Documentos distintos con " + fuente["texto"] + ".",
        ),
        ("De cada 10 inscriptos", "(los dos anteriores)", "Vinieron ÷ se anotaron × 10, redondeado."),
    ]

    if anio_anterior is not None:
        filas += [
            (
                "Variación (%)",
                "(Vinieron de los dos años)",
                f"(Vinieron {anio} − Vinieron {anio_anterior}) ÷ Vinieron {anio_anterior}.",
            ),
            (
                f"Volvieron de {anio_anterior}",
                f"{codigo('documento')} en {anio_anterior} y {anio}",
                "Documentos que vinieron a las dos ediciones.",
            ),
            (
                "Grupo que más bajó o subió",
                f"{codigo('Rol principal')}",
                "Cada opción del formulario se asigna a un grupo comparable entre años; "
                "se compara cuántas personas de cada grupo vinieron. Un cambio menor a 5 "
                "personas no se menciona.",
            ),
            (
                "Tendencia",
                "(Vinieron de cada año)",
                "Regresión lineal sobre las ediciones guardadas; necesita al menos 3.",
            ),
        ]

    return filas


def tabla_que_cambio(anio, anio_anterior):

    return [
        (
            "Diferencia por grupo",
            f"{codigo('Rol principal')} + {codigo('documento')} + asistencia",
            f"Personas que vinieron en {anio} menos las que vinieron en {anio_anterior}, "
            "por grupo comparable (cada opción del formulario se asigna a un grupo). "
            "El titular menciona un grupo solo si cambió en 5 personas o más.",
        ),
        (
            "Carreras",
            f"{codigo('Investigador Carreras')}",
            "Una celda puede tener varias carreras separadas por coma: se separan y cada "
            "persona cuenta en cada una. «Otro» se agrupa como «Otras áreas».",
        ),
        (
            f"Volvieron de {anio_anterior}",
            f"{codigo('documento')} en {anio_anterior} y {anio}",
            "Documentos que vinieron a las dos ediciones.",
        ),
    ]


def tabla_proxima(tendencia, anio):

    filas = [
        (
            "Meta automática",
            "(Vinieron de la última edición)",
            f"Superar a las personas que vinieron en {anio}. Se puede cambiar.",
        ),
    ]

    if not tendencia["suficiente"]:
        filas.append((
            "Estimación",
            "(Vinieron de cada año)",
            f"Necesita al menos {tendencia['anios_necesarios']} ediciones; hoy hay "
            f"{tendencia['anios_disponibles']}.",
        ))

    if tendencia["suficiente"]:
        r2 = f"{tendencia['r2']:.2f}".replace(".", ",")
        filas += [
            (
                f"Estimación {tendencia['proximo_anio']}",
                "(Vinieron de cada año)",
                f"Regresión lineal sobre {tendencia['anios_disponibles']} ediciones: "
                f"{tendencia['proyeccion']:.0f} personas (en el titular, redondeado a decenas).",
            ),
            (
                "R²",
                "—",
                f"{r2}: cuánto de la variación entre años explica la línea. Con pocas "
                "ediciones la confianza es baja; es orientativo.",
            ),
        ]

    return filas


# --------------------------------------------------
# C. PASO A PASO DE "VINIERON"
# --------------------------------------------------


def paso_a_paso_historico(df_anio, fuente):

    registros = len(df_anio)
    personas = df_anio["documento"].dropna().nunique()
    vinieron = (
        df_anio[df_anio["asistio"].astype(bool)]["documento"]
        .dropna()
        .nunique()
    )

    repetidas = registros - personas

    return [
        f"{formatear_numero(registros)} registros guardados de la edición",
        f"→ {formatear_numero(personas)} personas distintas por {codigo('documento')}"
        + (f" ({formatear_numero(repetidas)} inscripciones repetidas)" if repetidas else ""),
        f"→ {formatear_numero(vinieron)} con {fuente['texto']}",
    ]


def paso_a_paso_carga(df_original, df_limpio, columnas_dias):

    filas_excel = len(df_original)
    filas_limpias = len(df_limpio)
    personas = df_limpio["documento"].dropna().nunique()
    vinieron = (
        df_limpio[df_limpio["asistio"].astype(bool)]["documento"]
        .dropna()
        .nunique()
    )

    pasos = [f"{formatear_numero(filas_excel)} filas en el Excel"]

    if filas_limpias < filas_excel:
        pasos.append(
            f"→ {formatear_numero(filas_limpias)} al quitar filas repetidas o vacías"
        )

    repetidas = filas_limpias - personas

    pasos.append(
        f"→ {formatear_numero(personas)} personas distintas por {codigo('documento')}"
        + (f" ({formatear_numero(repetidas)} inscripciones repetidas)" if repetidas else "")
    )

    if columnas_dias:

        pasos.append(
            f"→ {formatear_numero(vinieron)} con al menos un «Si» en "
            + ", ".join(codigo(c) for c in columnas_dias)
        )

        # Días en que nadie figura presente: suele ser un dato que
        # falta cargar, y cambia mucho el total.
        sin_asistencia = [
            c.replace("Asistencia ", "")
            for c in columnas_dias
            if not df_original[c].astype(str).str.strip().str.lower().eq("si").any()
        ]

        if sin_asistencia:
            pasos.append(
                "⚠ Sin ningún «Si»: " + ", ".join(sin_asistencia)
                + ". Si hubo actividad esos días, falta cargar la asistencia."
            )

    else:

        pasos.append(
            f"→ {formatear_numero(vinieron)} con {codigo('isPresent')} en verdadero "
            "(el Excel no trae asistencia por día)"
        )

    return pasos
