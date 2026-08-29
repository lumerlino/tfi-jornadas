import random
import uuid

import pandas as pd


nombres = [
    "Ana", "Bruno", "Carla", "Diego", "Elena", "Franco", "Gabriela",
    "Hernan", "Ines", "Javier", "Karina", "Leandro", "Marina", "Nicolas",
    "Olga", "Pablo", "Rocio", "Sergio", "Tamara", "Ulises"
]

apellidos = [
    "Aguirre", "Benitez", "Cabrera", "Duarte", "Espinoza", "Ferrari",
    "Godoy", "Herrera", "Ibarra", "Juarez", "Lopez", "Medina", "Nunez",
    "Ortiz", "Paz", "Quiroga", "Rios", "Salazar", "Toledo", "Vera"
]

roles_principales = [
    "Estudiante de grado",
    "Docente-Investigador/a",
    "Estudiante de posgrado",
    "Graduado",
    "No docente",
    "Otro"
]

pesos_roles = [65, 18, 6, 6, 3, 2]

carreras_investigador = [
    "Lic. en C y T de los Alimentos",
    "Lic. en Sistemas",
    "Lic. en Economía empresarial",
    "Lic. en Turismo",
    "Lic. en Gestión ambiental Urbana",
    "Lic. en Logística"
]

tipos_inscripcion = [
    "Participante de grupo de investigación",
    "Asistente"
]

fuentes = [
    "Interno",
    "Externo excel"
]

fechas_jornada = [
    "2026-09-10",
    "2026-09-11",
    "2026-09-12"
]


random.seed(42)


# --------------------------------------------------
# GENERACIÓN DE PERSONAS INSCRIPTAS
# --------------------------------------------------

registros = []

for i in range(400):

    nombre = random.choice(nombres)
    apellido = random.choice(apellidos)

    documento = random.randint(20_000_000, 45_000_000)

    mail = (
        f"{nombre.split()[0].lower()}.{apellido.split()[0].lower()}"
        f"{i}@example.com"
    )

    miembro_unla = random.choices(
        ["Si", "No"],
        weights=[80, 20],
        k=1
    )[0]

    rol_principal = random.choices(
        roles_principales,
        weights=pesos_roles,
        k=1
    )[0]

    otro_rol_principal = (
        "Colaborador externo del proyecto"
        if rol_principal == "Otro"
        else None
    )

    investigador_carreras = (
        random.choice(carreras_investigador)
        if rol_principal in (
            "Docente-Investigador/a",
            "Estudiante de posgrado"
        )
        else None
    )

    tipo_inscripcion = random.choices(
        tipos_inscripcion,
        weights=[60, 40],
        k=1
    )[0]

    source = random.choices(
        fuentes,
        weights=[75, 25],
        k=1
    )[0]

    is_welcome_mail_sent = random.random() < 0.9

    # Asistencia real día por día
    probabilidad_asistencia = random.uniform(0.3, 0.9)

    asistencia_por_dia = {
        f"Asistencia {fecha}": (
            "Si"
            if random.random() < probabilidad_asistencia
            else "No"
        )
        for fecha in fechas_jornada
    }

    asistio_algun_dia = any(
        valor == "Si"
        for valor in asistencia_por_dia.values()
    )

    is_assistance_certify_sent = (
        asistio_algun_dia and random.random() < 0.7
    )

    registro = {
        "Nombre/s": nombre,
        "Apellido/s": apellido,
        "documento": documento,
        "mail": mail,
        "Miembro UNLa": miembro_unla,
        "Rol principal": rol_principal,
        "Otro Rol principal": otro_rol_principal,
        "Investigador Carreras": investigador_carreras,
        "Otro Investigador Carreras": None,
        "Tipo inscripción": tipo_inscripcion,
        "Source": source,
        "IsWelcomeMailSent": is_welcome_mail_sent,
        "QRCode": str(uuid.uuid4()),
        "isPresent": asistio_algun_dia,
        "IsAssistanceCertifySent": is_assistance_certify_sent,
        **asistencia_por_dia
    }

    registros.append(registro)


df = pd.DataFrame(registros)


# --------------------------------------------------
# ERRORES FICTICIOS PARA PROBAR CALIDAD DE DATOS
# --------------------------------------------------

# Documentos faltantes
df.loc[0:2, "documento"] = None

# Mails con formato inválido
df.loc[3:4, "mail"] = "sin-arroba-en-el-mail"

# Miembro UNLa / Rol principal / Tipo inscripción faltantes
df.loc[5:7, ["Miembro UNLa", "Rol principal", "Tipo inscripción"]] = None

# isPresent inconsistente con la asistencia real por día
# (para poner a prueba la validación de coherencia)
df.loc[8, "isPresent"] = not df.loc[8, "isPresent"]
df.loc[9, "isPresent"] = not df.loc[9, "isPresent"]

# Documento duplicado entre dos personas distintas
df.loc[11, "documento"] = df.loc[10, "documento"]

# Filas completamente duplicadas
df.loc[13] = df.loc[14]


# --------------------------------------------------
# GENERACIÓN DEL EXCEL
# --------------------------------------------------

df.to_excel(
    "data/demo/datos_jornadas_v2.xlsx",
    index=False
)


print("Archivo generado correctamente")
print("Cantidad de inscripciones:", len(df))
print(
    "Cantidad de personas únicas (documento):",
    df["documento"].nunique()
)
