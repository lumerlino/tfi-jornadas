import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

CARPETA_JORNADAS = BASE_DIR / "data" / "jornadas"


def _carpeta_cargas(anio):

    return CARPETA_JORNADAS / str(anio) / "cargas"


def obtener_proximo_numero_carga(carpeta_cargas):

    archivos = list(carpeta_cargas.glob("carga_*.xlsx"))

    numeros = []

    for archivo in archivos:

        try:
            numeros.append(int(archivo.stem.split("_")[-1]))
        except ValueError:
            continue

    if not numeros:
        return 1

    return max(numeros) + 1


def guardar_edicion(df_limpio, anio, fecha_inicio, fecha_fin, es_demo=False):

    carpeta_jornada = CARPETA_JORNADAS / str(anio)
    carpeta_cargas = _carpeta_cargas(anio)

    carpeta_cargas.mkdir(parents=True, exist_ok=True)

    metadata = {
        "anio": anio,
        "fecha_inicio": str(fecha_inicio),
        "fecha_fin": str(fecha_fin),
        "es_demo": es_demo
    }

    with open(
        carpeta_jornada / "metadata.json",
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(metadata, archivo, ensure_ascii=False, indent=4)

    numero_carga = obtener_proximo_numero_carga(carpeta_cargas)

    ruta_excel = carpeta_cargas / f"carga_{numero_carga:03d}.xlsx"

    df_limpio.to_excel(ruta_excel, index=False)

    return ruta_excel


def cargar_historico():

    if not CARPETA_JORNADAS.exists():
        return pd.DataFrame()

    dataframes = []

    for carpeta_jornada in sorted(CARPETA_JORNADAS.iterdir()):

        if not carpeta_jornada.is_dir():
            continue

        ruta_metadata = carpeta_jornada / "metadata.json"
        carpeta_cargas = carpeta_jornada / "cargas"

        if not ruta_metadata.exists() or not carpeta_cargas.exists():
            continue

        with open(ruta_metadata, encoding="utf-8") as archivo:
            metadata = json.load(archivo)

        cargas = sorted(carpeta_cargas.glob("carga_*.xlsx"))

        if not cargas:
            continue

        ultima_carga = cargas[-1]

        df = pd.read_excel(ultima_carga)

        df["anio"] = metadata["anio"]
        df["es_demo"] = metadata.get("es_demo", False)
        df["fecha_inicio_jornada"] = metadata["fecha_inicio"]
        df["fecha_fin_jornada"] = metadata["fecha_fin"]

        dataframes.append(df)

    if not dataframes:
        return pd.DataFrame()

    return pd.concat(dataframes, ignore_index=True)
