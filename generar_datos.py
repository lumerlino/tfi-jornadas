import pandas as pd
import random
from datetime import datetime, timedelta


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
        "fecha": "10/09/2026",
        "hora_inicio": "09:00",
        "hora_fin": "10:30",
    },
    {
        "actividad": "Taller IA",
        "tipo_actividad": "Taller",
        "tematica": "Inteligencia Artificial",
        "aula": "Laboratorio",
        "capacidad_aula": 40,
        "ocupacion_objetivo": 0.95,
        "fecha": "10/09/2026",
        "hora_inicio": "14:00",
        "hora_fin": "16:00",
    },
    {
        "actividad": "Ciencia de Datos",
        "tipo_actividad": "Conferencia",
        "tematica": "Ciencia de Datos",
        "aula": "Aula 1",
        "capacidad_aula": 100,
        "ocupacion_objetivo": 0.75,
        "fecha": "10/09/2026",
        "hora_inicio": "10:00",
        "hora_fin": "12:00",
    },
    {
        "actividad": "Mesa de Investigación",
        "tipo_actividad": "Mesa",
        "tematica": "Investigación",
        "aula": "Aula 2",
        "capacidad_aula": 60,
        "ocupacion_objetivo": 0.60,
        "fecha": "11/09/2026",
        "hora_inicio": "15:00",
        "hora_fin": "17:00",
    },
    {
        "actividad": "Cierre",
        "tipo_actividad": "Cierre",
        "tematica": "Institucional",
        "aula": "Auditorio",
        "capacidad_aula": 250,
        "ocupacion_objetivo": 0.70,
        "fecha": "12/09/2026",
        "hora_inicio": "10:00",
        "hora_fin": "12:00",
    }
]


datos = []
participantes = []

def calcular_peso_participante(participante, actividad):

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


    # Apertura y Cierre:
    # mantenemos un público más general

    return peso

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

        seleccionados.append(elegido)

        disponibles.remove(elegido)

    return seleccionados


# --------------------------------------------------
# CREACIÓN DE PARTICIPANTES
# --------------------------------------------------

# Creamos 400 participantes
for i in range(400):

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

    participantes.append(participante)


# --------------------------------------------------
# GENERACIÓN DE PARTICIPACIONES
# --------------------------------------------------

for actividad_elegida in actividades:

    cantidad_participantes = int(
        actividad_elegida["capacidad_aula"]
        * actividad_elegida["ocupacion_objetivo"]
    )

    participantes_actividad = seleccionar_participantes(
        participantes,
        actividad_elegida,
        cantidad_participantes
    )

    for participante_elegido in participantes_actividad:

        hora_inicio = datetime.strptime(
            actividad_elegida["hora_inicio"],
            "%H:%M"
        )

        hora_fin = datetime.strptime(
            actividad_elegida["hora_fin"],
            "%H:%M"
        )

        hora_ingreso = hora_inicio + timedelta(
            minutes=random.randint(-10, 15)
        )

        hora_egreso = hora_fin + timedelta(
            minutes=random.randint(-30, 10)
        )

        inscripto = random.choices(
            ["Sí", "No"],
            weights=[85, 15],
            k=1
        )[0]

        estado_qr = random.choices(
            ["Correcto", "Error"],
            weights=[95, 5],
            k=1
        )[0]

        punto_acceso = random.choices(
            [
                "Entrada principal",
                "Acceso lateral",
                "Auditorio"
            ],
            weights=[70, 20, 10],
            k=1
        )[0]

        registro = {
            "id_participante": participante_elegido["id_participante"],
            "tipo_participante": participante_elegido["tipo_participante"],
            "carrera": participante_elegido["carrera"],
            "institucion": participante_elegido["institucion"],

            "actividad": actividad_elegida["actividad"],
            "tipo_actividad": actividad_elegida["tipo_actividad"],
            "tematica": actividad_elegida["tematica"],
            "aula": actividad_elegida["aula"],
            "capacidad_aula": actividad_elegida["capacidad_aula"],

            "fecha": actividad_elegida["fecha"],
            "hora_inicio_actividad": actividad_elegida["hora_inicio"],
            "hora_fin_actividad": actividad_elegida["hora_fin"],
            "hora_ingreso": hora_ingreso.strftime("%H:%M"),
            "hora_egreso": hora_egreso.strftime("%H:%M"),

            "inscripto": inscripto,
            "asistio": "Sí",

            "estado_qr": estado_qr,
            "punto_acceso": punto_acceso,
        }

        datos.append(registro)


# --------------------------------------------------
# CREACIÓN DEL DATAFRAME
# --------------------------------------------------

df = pd.DataFrame(datos)


# --------------------------------------------------
# ERRORES FICTICIOS PARA PROBAR CALIDAD DE DATOS
# --------------------------------------------------

# Participantes sin identificador
df.loc[0:2, "id_participante"] = None

# Horas de ingreso faltantes
df.loc[3:5, "hora_ingreso"] = None

# Horas de egreso faltantes
df.loc[6:9, "hora_egreso"] = None

# Capacidades de aula inválidas
df.loc[10:12, "capacidad_aula"] = 0

# Estados QR inválidos
df.loc[13:15, "estado_qr"] = "Desconocido"

# Creamos algunas filas completamente duplicadas
df.loc[16] = df.loc[17]
df.loc[18] = df.loc[19]


# --------------------------------------------------
# GENERACIÓN DEL EXCEL
# --------------------------------------------------

df.to_excel(
    "data/demo/datos_jornadas_v2.xlsx",
    index=False
)


print("Archivo generado correctamente")
print("Cantidad de participaciones:", len(df))
print(
    "Cantidad de participantes únicos:",
    df["id_participante"].nunique()
)