import unicodedata

import pandas as pd


# --------------------------------------------------
# GRUPOS COMPARABLES DE CATEGORÍAS
#
# El formulario de inscripción cambia de un año a otro: en 2026
# "Rol principal" renombró opciones ("Docente-Investigador/a" ->
# "Docente-Investigador/a universitario"), fusionó otras ("Estudiante
# de grado" + "de posgrado" -> "Estudiante secundario/grado/posgrado")
# y agregó opciones por ocupación ("Trabajo en una empresa", ...).
# Para comparar años se usa un agrupamiento común: cada valor
# original del Excel pertenece a un grupo.
#
# Se aplica al LEER los datos: en la base queda el valor original,
# así que corregir un grupo acá recalcula todo sin recargar nada.
# Los valores salen de los Excel reales 2024-2026. Estructura pensada
# para pasar a una tabla editable en Supabase más adelante.
# --------------------------------------------------

COLUMNA_ROL = "Rol principal"
COLUMNA_GRUPO_ROL = "Grupo de rol"

OTROS_PERFILES = "Otros perfiles"
SIN_DATO = "Sin dato"

GRUPOS_ROL = {
    "Docentes-investigadores": [
        "Docente-Investigador/a",
        "Docente-Investigador/a universitario",
        "Docente externo investigador",
        "Investigadora Externa",
        "Integrante grupo de investigacion",
    ],
    "Estudiantes": [
        "Estudiante de grado",
        "Estudiante de posgrado",
        "Estudiante",
        "Estudiante secundario/grado/posgrado",
    ],
    "Graduados y profesionales": [
        "Graduado",
        "Profesional independiente",
        "Trabajo en una empresa",
        "Trabajo en una organización pública",
        "Trabajo en una organización no gubernamental",
    ],
    "No docentes": [
        "No docente",
        "No docente y docente",
    ],
    OTROS_PERFILES: [
        "Otro",
        "Otra",
    ],
}

# Grupos que no se usan para detectar cambios de definición: juntan
# respuestas sueltas o de texto libre que varían todos los años.
GRUPOS_SIN_CONTROL = {OTROS_PERFILES, SIN_DATO}

# Un valor con menos respuestas que esto no cuenta como parte de la
# definición del grupo en ese año (evita avisos por respuestas sueltas).
MINIMO_PARA_DEFINICION = 3


def normalizar(valor):

    # Comparación tolerante: sin mayúsculas, tildes ni espacios de más.

    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ""

    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(c for c in texto if not unicodedata.combining(c))

    return " ".join(texto.casefold().split())


_GRUPO_POR_VALOR = {
    normalizar(valor): grupo
    for grupo, valores in GRUPOS_ROL.items()
    for valor in valores
}


def grupo_de_rol(valor):

    clave = normalizar(valor)

    if clave in ("", "nan", "none", "<na>"):
        return SIN_DATO

    return _GRUPO_POR_VALOR.get(clave, OTROS_PERFILES)


def agregar_grupos(df):

    # Agrega la columna "Grupo de rol" a partir de "Rol principal".

    df = df.copy()

    if COLUMNA_ROL in df.columns:
        df[COLUMNA_GRUPO_ROL] = df[COLUMNA_ROL].map(grupo_de_rol)
    else:
        df[COLUMNA_GRUPO_ROL] = SIN_DATO

    return df


def roles_sin_grupo(df):

    # Valores de "Rol principal" que ningún grupo reconoce (van a
    # "Otros perfiles"). Devuelve {valor: cantidad}, de más a menos.

    if COLUMNA_ROL not in df.columns:
        return {}

    valores = df[COLUMNA_ROL].dropna().astype(str).str.strip()
    valores = valores[valores != ""]

    desconocidos = valores[~valores.map(normalizar).isin(_GRUPO_POR_VALOR)]

    return desconocidos.value_counts().to_dict()


def _definicion(df, anio):

    # {grupo: conjunto de valores originales con peso suficiente}
    del_anio = df[df["anio"] == anio]

    conteo = (
        del_anio.dropna(subset=[COLUMNA_ROL])
        .assign(_valor=lambda d: d[COLUMNA_ROL].map(normalizar))
        .groupby([COLUMNA_GRUPO_ROL, "_valor"])
        .size()
    )

    definicion = {}

    for (grupo, valor), cantidad in conteo.items():
        if grupo in GRUPOS_SIN_CONTROL or cantidad < MINIMO_PARA_DEFINICION:
            continue
        definicion.setdefault(grupo, set()).add(valor)

    return definicion


def cambios_de_definicion(df, anio_anterior, anio):

    # Grupos cuyo conjunto de opciones del formulario cambió entre los
    # dos años (renombres, fusiones u opciones nuevas). Si hay alguno,
    # la comparación por grupo entre esos años es aproximada.
    # Devuelve {grupo: (valores de antes, valores de ahora)}.

    antes = _definicion(df, anio_anterior)
    ahora = _definicion(df, anio)

    originales = {}
    for valor in df[COLUMNA_ROL].dropna().astype(str):
        originales.setdefault(normalizar(valor), valor.strip())

    cambios = {}

    for grupo in sorted(set(antes) | set(ahora)):

        valores_antes = antes.get(grupo, set())
        valores_ahora = ahora.get(grupo, set())

        if valores_antes and valores_ahora and valores_antes != valores_ahora:
            cambios[grupo] = (
                sorted(originales[v] for v in valores_antes),
                sorted(originales[v] for v in valores_ahora),
            )

    return cambios
