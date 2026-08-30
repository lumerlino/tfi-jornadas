import pandas as pd

from utils.limpieza_datos import detectar_columnas_asistencia


# --------------------------------------------------
# Métricas/gráficos válidos según el tipo de dato
# detectado. "identificador" y "texto_libre" quedan
# sin opciones a propósito: alta cardinalidad de texto
# (documento, mail, nombre) no se ofrece como filtro
# ni gráfico, por privacidad.
# --------------------------------------------------

METRICAS_POR_TIPO = {
    "categorica": ["Barras", "Torta", "Ninguna"],
    "numerica": ["Histograma", "Resumen estadístico", "Ninguna"],
    "booleana": ["Tasa (%)", "Ninguna"],
    "fecha": ["Evolución temporal", "Ninguna"],
    "identificador": [],
    "texto_libre": []
}


def clasificar_columna(serie):

    serie_no_nula = serie.dropna()

    if len(serie_no_nula) == 0:
        return "texto_libre"

    if pd.api.types.is_bool_dtype(serie):
        return "booleana"

    valores_booleanos = {"si", "no", "sí", "true", "false"}

    valores_unicos_texto = {
        str(valor).strip().lower()
        for valor in serie_no_nula.unique()
    }

    if valores_unicos_texto <= valores_booleanos:
        return "booleana"

    if pd.api.types.is_numeric_dtype(serie):
        return "numerica"

    if pd.api.types.is_datetime64_any_dtype(serie):
        return "fecha"

    # Texto: categórica, identificador o texto libre según
    # cuánto se repiten los valores (cardinalidad).
    cardinalidad = serie_no_nula.nunique()
    proporcion_unica = cardinalidad / len(serie_no_nula)

    if proporcion_unica > 0.9 and cardinalidad > 15:
        return "identificador"

    if cardinalidad <= 20:
        return "categorica"

    return "texto_libre"


def columnas_no_mapeadas(df, columnas_conocidas):

    columnas_conocidas = set(columnas_conocidas)
    columnas_asistencia = set(detectar_columnas_asistencia(df))

    return [
        columna
        for columna in df.columns
        if columna not in columnas_conocidas
        and columna not in columnas_asistencia
    ]
