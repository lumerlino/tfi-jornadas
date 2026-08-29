from utils.limpieza_datos import limpiar_datos


def preparar_datos(df):

    df_limpio, asistencia_larga, reporte_antes, reporte_despues = (
        limpiar_datos(df)
    )

    return df_limpio, reporte_antes, reporte_despues
