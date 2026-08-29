import random
import shutil
import uuid
from pathlib import Path

import pandas as pd

from utils.limpieza_datos import limpiar_datos, detectar_columnas_asistencia
from utils.historico_local import guardar_edicion, CARPETA_JORNADAS


BASE_DIR = Path(__file__).resolve().parent

RUTA_JORNADAS_INVESTIGACION = Path(
    r"K:\Libros\TFI\JornadasInvestigacion\JornadaDeInvestigacion"
)

RUTA_DEMO_2026 = BASE_DIR / "data" / "demo" / "datos_jornadas_v2.xlsx"


# --------------------------------------------------
# ANONIMIZACIÓN DE LOS ARCHIVOS REALES (2024 / 2025)
# --------------------------------------------------
# Los archivos originales tienen documento/nombre/mail reales
# de personas reales. Antes de guardarlos en data/jornadas (que
# se sube a git) se reemplazan por valores ficticios, con un
# mapeo consistente entre ambos años: la misma persona real
# conserva la misma identidad ficticia en los dos archivos, para
# que la tasa de repetición calculada sobre estos datos siga
# siendo representativa de la realidad.
# --------------------------------------------------

nombres_ficticios = [
    "Ana", "Bruno", "Carla", "Diego", "Elena", "Franco", "Gabriela",
    "Hernan", "Ines", "Javier", "Karina", "Leandro", "Marina", "Nicolas",
    "Olga", "Pablo", "Rocio", "Sergio", "Tamara", "Ulises"
]

apellidos_ficticios = [
    "Aguirre", "Benitez", "Cabrera", "Duarte", "Espinoza", "Ferrari",
    "Godoy", "Herrera", "Ibarra", "Juarez", "Lopez", "Medina", "Nunez",
    "Ortiz", "Paz", "Quiroga", "Rios", "Salazar", "Toledo", "Vera"
]


def anonimizar_ediciones(dataframes):

    random.seed(2024)

    documentos_reales = sorted({
        str(valor)
        for df in dataframes
        for valor in df["documento"].dropna().tolist()
    })

    mapeo = {}

    for indice, documento_real in enumerate(documentos_reales):

        nombre = random.choice(nombres_ficticios)
        apellido = random.choice(apellidos_ficticios)

        mapeo[documento_real] = {
            "documento": str(90_000_000 + indice),
            "Nombre/s": nombre,
            "Apellido/s": apellido,
            "mail": (
                f"{nombre.lower()}.{apellido.lower()}{indice}"
                f"@example.com"
            )
        }

    resultado = []

    for df in dataframes:

        df = df.copy()
        documentos_originales = df["documento"].astype(str)

        for campo in ["documento", "Nombre/s", "Apellido/s", "mail"]:

            df[campo] = documentos_originales.map(
                lambda doc: mapeo.get(doc, {}).get(campo)
            )

        if "QRCode" in df.columns:

            df["QRCode"] = [
                str(uuid.uuid4())
                for _ in range(len(df))
            ]

        resultado.append(df)

    return resultado


# --------------------------------------------------
# GUARDADO DE CADA EDICIÓN COMO FIXTURE LOCAL
# --------------------------------------------------

def limpiar_carpeta_jornada(anio):

    carpeta = CARPETA_JORNADAS / str(anio)

    if carpeta.exists():
        shutil.rmtree(carpeta)


def fechas_desde_asistencia(df, anio_por_defecto):

    columnas = detectar_columnas_asistencia(df)

    if not columnas:
        return f"{anio_por_defecto}-01-01", f"{anio_por_defecto}-12-31"

    fechas = sorted(
        columna.replace("Asistencia ", "")
        for columna in columnas
    )

    return fechas[0], fechas[-1]


def procesar_edicion(anio, df_crudo, es_demo):

    limpiar_carpeta_jornada(anio)

    fecha_inicio, fecha_fin = fechas_desde_asistencia(df_crudo, anio)

    df_limpio, _, _, _ = limpiar_datos(df_crudo)

    ruta = guardar_edicion(
        df_limpio,
        anio,
        fecha_inicio,
        fecha_fin,
        es_demo=es_demo
    )

    print(
        f"Edición {anio} "
        f"({'demo' if es_demo else 'real'}) guardada en {ruta}"
    )

    print(
        f"  Personas: {df_limpio['documento'].nunique()} | "
        f"Asistieron: {int(df_limpio['asistio'].sum())}"
    )

    return df_limpio


if __name__ == "__main__":

    ruta_2024 = (
        RUTA_JORNADAS_INVESTIGACION
        / "JIDDPyT 2024 event_responses.xlsx"
    )

    ruta_2025 = (
        RUTA_JORNADAS_INVESTIGACION
        / "JIDDPyT 2025 event_responses.xlsx"
    )

    if not ruta_2024.exists() or not ruta_2025.exists():

        raise SystemExit(
            f"No se encontraron los archivos reales en "
            f"{RUTA_JORNADAS_INVESTIGACION}. Este script espera "
            f"'JIDDPyT 2024 event_responses.xlsx' y "
            f"'JIDDPyT 2025 event_responses.xlsx' ahí."
        )

    df_2024_crudo = pd.read_excel(ruta_2024)
    df_2025_crudo = pd.read_excel(ruta_2025)

    df_2024_anonimo, df_2025_anonimo = anonimizar_ediciones(
        [df_2024_crudo, df_2025_crudo]
    )

    df_2024_limpio = procesar_edicion(
        2024, df_2024_anonimo, es_demo=False
    )

    df_2025_limpio = procesar_edicion(
        2025, df_2025_anonimo, es_demo=False
    )

    if not RUTA_DEMO_2026.exists():

        raise SystemExit(
            f"No se encontró {RUTA_DEMO_2026}. "
            f"Ejecutá generar_datos.py primero."
        )

    df_2026_crudo = pd.read_excel(RUTA_DEMO_2026)

    df_2026_limpio = procesar_edicion(
        2026, df_2026_crudo, es_demo=True
    )

    documentos_2024 = set(
        df_2024_limpio[df_2024_limpio["asistio"]]["documento"].dropna()
    )

    documentos_2025 = set(
        df_2025_limpio[df_2025_limpio["asistio"]]["documento"].dropna()
    )

    repiten = documentos_2024 & documentos_2025

    print()
    print("-" * 50)
    print("Resumen del fixture de histórico")
    print("-" * 50)
    print(f"2024 (real): {len(documentos_2024)} asistentes")
    print(f"2025 (real): {len(documentos_2025)} asistentes")
    print(f"Repiten 2024 -> 2025: {len(repiten)}")
    print(
        f"2026 (demo): "
        f"{int(df_2026_limpio['asistio'].sum())} asistentes"
    )
