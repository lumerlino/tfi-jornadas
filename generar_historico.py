import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# RUTAS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

CARPETA_JORNADAS = (
    BASE_DIR
    / "data"
    / "jornadas"
)


# --------------------------------------------------
# CONFIGURACIÓN DE CADA AÑO
# --------------------------------------------------

configuraciones_jornadas = {
    2024: {
        "cantidad_participantes": 300,
        "error_qr": [90, 10],
        "factor_ocupacion": 0.85
    },

    2025: {
        "cantidad_participantes": 350,
        "error_qr": [94, 6],
        "factor_ocupacion": 0.93
    },

    2026: {
        "cantidad_participantes": 400,
        "error_qr": [97, 3],
        "factor_ocupacion": 1.00
    }
}


# --------------------------------------------------
# DATOS BASE
# --------------------------------------------------

tipos_participante = [
    "Estudiante",
    "Docente",
    "Investigador",
    "Graduado",
    "Externo"
]

carreras = [
    "Sistemas",
    "Economía",
    "Turismo",
    "Alimentos",
    "Diseño"
]

instituciones = [
    "UNLa",
    "UBA",
    "UNQ",
    "UNLZ",
    "Otra"
]


actividades = [
    {
        "actividad": "Apertura",
        "tipo_actividad": "Apertura",
        "tematica": "Institucional",
        "aula": "Auditorio",
        "capacidad_aula": 250,
        "ocupacion_objetivo": 0.85,
        "fecha": "10/09",
        "hora_inicio": "09:00",
        "hora_fin": "10:30"
    },
    {
        "actividad": "Taller IA",
        "tipo_actividad": "Taller",
        "tematica": "Inteligencia Artificial",
        "aula": "Laboratorio",
        "capacidad_aula": 40,
        "ocupacion_objetivo": 0.95,
        "fecha": "10/09",
        "hora_inicio": "14:00",
        "hora_fin": "16:00"
    },
    {
        "actividad": "Ciencia de Datos",
        "tipo_actividad": "Conferencia",
        "tematica": "Ciencia de Datos",
        "aula": "Aula 1",
        "capacidad_aula": 100,
        "ocupacion_objetivo": 0.75,
        "fecha": "10/09",
        "hora_inicio": "10:00",
        "hora_fin": "12:00"
    },
    {
        "actividad": "Mesa de Investigación",
        "tipo_actividad": "Mesa",
        "tematica": "Investigación",
        "aula": "Aula 2",
        "capacidad_aula": 60,
        "ocupacion_objetivo": 0.60,
        "fecha": "11/09",
        "hora_inicio": "15:00",
        "hora_fin": "17:00"
    },
    {
        "actividad": "Cierre",
        "tipo_actividad": "Cierre",
        "tematica": "Institucional",
        "aula": "Auditorio",
        "capacidad_aula": 250,
        "ocupacion_objetivo": 0.70,
        "fecha": "12/09",
        "hora_inicio": "10:00",
        "hora_fin": "12:00"
    }
]


# --------------------------------------------------
# GENERACIÓN DE PARTICIPANTES
# --------------------------------------------------

def generar_participantes(cantidad):

    participantes = []

    for i in range(cantidad):

        tipo_participante = random.choices(
            tipos_participante,
            weights=[55, 20, 10, 10, 5],
            k=1
        )[0]

        carrera = random.choices(
            carreras,
            weights=[35, 20, 18, 15, 12],
            k=1
        )[0]

        institucion = random.choices(
            instituciones,
            weights=[70, 8, 7, 7, 8],
            k=1
        )[0]

        participante = {
            "id_participante": f"P{i + 1:04d}",
            "tipo_participante": tipo_participante,
            "carrera": carrera,
            "institucion": institucion
        }

        participantes.append(
            participante
        )

    return participantes


# --------------------------------------------------
# PESO SEGÚN ACTIVIDAD
# --------------------------------------------------

def calcular_peso_participante(
    participante,
    actividad
):

    peso = 1


    # Taller IA
    if actividad["actividad"] == "Taller IA":

        if participante["carrera"] == "Sistemas":
            peso += 5

        if participante["tipo_participante"] == "Estudiante":
            peso += 3


    # Ciencia de Datos
    elif actividad["actividad"] == "Ciencia de Datos":

        if participante["carrera"] == "Sistemas":
            peso += 4

        if participante["carrera"] == "Economía":
            peso += 2

        if participante["tipo_participante"] == "Estudiante":
            peso += 2


    # Mesa de Investigación
    elif actividad["actividad"] == "Mesa de Investigación":

        if participante["tipo_participante"] == "Docente":
            peso += 5

        if participante["tipo_participante"] == "Investigador":
            peso += 6


    return peso


# --------------------------------------------------
# SELECCIÓN DE PARTICIPANTES
# --------------------------------------------------

def seleccionar_participantes(
    participantes,
    actividad,
    cantidad
):

    disponibles = participantes.copy()

    seleccionados = []


    while len(seleccionados) < cantidad:

        pesos = [
            calcular_peso_participante(
                participante,
                actividad
            )
            for participante in disponibles
        ]

        elegido = random.choices(
            disponibles,
            weights=pesos,
            k=1
        )[0]

        seleccionados.append(
            elegido
        )

        disponibles.remove(
            elegido
        )


    return seleccionados


# --------------------------------------------------
# GENERAR UNA JORNADA
# --------------------------------------------------

def generar_jornada(
    anio,
    configuracion
):

    participantes = generar_participantes(
        configuracion[
            "cantidad_participantes"
        ]
    )

    datos = []


    for actividad_elegida in actividades:

        ocupacion_real = (
            actividad_elegida[
                "ocupacion_objetivo"
            ]
            * configuracion[
                "factor_ocupacion"
            ]
        )


        cantidad_participantes = int(
            actividad_elegida[
                "capacidad_aula"
            ]
            * ocupacion_real
        )


        cantidad_participantes = min(
            cantidad_participantes,
            len(participantes)
        )


        participantes_actividad = (
            seleccionar_participantes(
                participantes,
                actividad_elegida,
                cantidad_participantes
            )
        )


        for participante_elegido in participantes_actividad:

            hora_inicio = datetime.strptime(
                actividad_elegida[
                    "hora_inicio"
                ],
                "%H:%M"
            )

            hora_fin = datetime.strptime(
                actividad_elegida[
                    "hora_fin"
                ],
                "%H:%M"
            )


            hora_ingreso = (
                hora_inicio
                + timedelta(
                    minutes=random.randint(
                        -10,
                        15
                    )
                )
            )


            hora_egreso = (
                hora_fin
                + timedelta(
                    minutes=random.randint(
                        -30,
                        10
                    )
                )
            )


            inscripto = random.choices(
                [
                    "Sí",
                    "No"
                ],
                weights=[
                    85,
                    15
                ],
                k=1
            )[0]


            estado_qr = random.choices(
                [
                    "Correcto",
                    "Error"
                ],
                weights=configuracion[
                    "error_qr"
                ],
                k=1
            )[0]


            punto_acceso = random.choices(
                [
                    "Entrada principal",
                    "Acceso lateral",
                    "Auditorio"
                ],
                weights=[
                    70,
                    20,
                    10
                ],
                k=1
            )[0]


            fecha_completa = (
                actividad_elegida[
                    "fecha"
                ]
                + f"/{anio}"
            )


            registro = {
                "id_participante": participante_elegido[
                    "id_participante"
                ],

                "tipo_participante": participante_elegido[
                    "tipo_participante"
                ],

                "carrera": participante_elegido[
                    "carrera"
                ],

                "institucion": participante_elegido[
                    "institucion"
                ],

                "actividad": actividad_elegida[
                    "actividad"
                ],

                "tipo_actividad": actividad_elegida[
                    "tipo_actividad"
                ],

                "tematica": actividad_elegida[
                    "tematica"
                ],

                "aula": actividad_elegida[
                    "aula"
                ],

                "capacidad_aula": actividad_elegida[
                    "capacidad_aula"
                ],

                "fecha": fecha_completa,

                "hora_inicio_actividad": actividad_elegida[
                    "hora_inicio"
                ],

                "hora_fin_actividad": actividad_elegida[
                    "hora_fin"
                ],

                "hora_ingreso": hora_ingreso.strftime(
                    "%H:%M"
                ),

                "hora_egreso": hora_egreso.strftime(
                    "%H:%M"
                ),

                "inscripto": inscripto,

                "asistio": "Sí",

                "estado_qr": estado_qr,

                "punto_acceso": punto_acceso
            }


            datos.append(
                registro
            )


    return pd.DataFrame(
        datos
    )


# --------------------------------------------------
# OBTENER PRÓXIMO NÚMERO DE CARGA
# --------------------------------------------------

def obtener_proximo_numero_carga(
    carpeta_cargas
):

    archivos = list(
        carpeta_cargas.glob(
            "carga_*.xlsx"
        )
    )


    numeros = []


    for archivo in archivos:

        try:

            numero = int(
                archivo.stem
                .split("_")[-1]
            )

            numeros.append(
                numero
            )

        except ValueError:

            continue


    if not numeros:

        return 1


    return max(numeros) + 1


# --------------------------------------------------
# GUARDAR JORNADA
# --------------------------------------------------

def guardar_jornada(
    anio,
    df
):

    carpeta_jornada = (
        CARPETA_JORNADAS
        / str(anio)
    )

    carpeta_cargas = (
        carpeta_jornada
        / "cargas"
    )


    carpeta_cargas.mkdir(
        parents=True,
        exist_ok=True
    )


    # --------------------------------------------------
    # METADATA
    # --------------------------------------------------

    metadata = {
        "anio": anio,
        "fecha_inicio": f"{anio}-09-10",
        "fecha_fin": f"{anio}-09-12"
    }


    ruta_metadata = (
        carpeta_jornada
        / "metadata.json"
    )


    with open(
        ruta_metadata,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            metadata,
            archivo,
            ensure_ascii=False,
            indent=4
        )


    # --------------------------------------------------
    # NUEVA CARGA
    # --------------------------------------------------

    numero_carga = (
        obtener_proximo_numero_carga(
            carpeta_cargas
        )
    )


    ruta_excel = (
        carpeta_cargas
        / f"carga_{numero_carga:03d}.xlsx"
    )


    df.to_excel(
        ruta_excel,
        index=False
    )


    return ruta_excel


# --------------------------------------------------
# GENERACIÓN DEL HISTÓRICO
# --------------------------------------------------

for anio, configuracion in configuraciones_jornadas.items():

    df = generar_jornada(
        anio,
        configuracion
    )


    ruta_generada = guardar_jornada(
        anio,
        df
    )


    print(
        f"Jornada {anio} generada correctamente"
    )

    print(
        f"Archivo: {ruta_generada}"
    )

    print(
        "Cantidad de participaciones:",
        len(df)
    )

    print(
        "Cantidad de participantes únicos:",
        df[
            "id_participante"
        ].nunique()
    )

    print(
        "-" * 50
    )