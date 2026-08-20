import pandas as pd


def cargar_datos_demo():
    return pd.read_excel(
        "data/demo/datos_jornadas_v2.xlsx"
    )


def cargar_excel_usuario(archivo):
    return pd.read_excel(archivo)