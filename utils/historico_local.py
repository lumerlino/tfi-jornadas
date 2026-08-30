import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

CARPETA_JORNADAS = BASE_DIR / "data" / "jornadas"


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
