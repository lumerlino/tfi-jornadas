import streamlit as st


def mostrar_interpretacion_calidad(datos):
    documentos_faltantes = datos["documentos_faltantes"]
    roles_faltantes = datos["roles_faltantes"]
    reinscripciones = datos["reinscripciones"]
    mails_invalidos = datos["mails_invalidos"]
    tipos_inscripcion_faltantes = datos["tipos_inscripcion_faltantes"]
    filas_duplicadas = datos["filas_duplicadas"]
    welcome_mail_no_enviado = datos["welcome_mail_no_enviado"]
    inconsistencias_asistencia = datos["inconsistencias_asistencia"]

    st.markdown(
        "#### Interpretación de las validaciones"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Documento informado**")
        st.caption(
            "Se considera válido cuando el registro tiene un número de documento cargado. "
            "Los registros sin documento se consideran incompletos para identificar participantes únicos."
        )

        if documentos_faltantes == 0:
            st.success("Todos los registros tienen documento informado.")
        else:
            st.warning(
                f"{documentos_faltantes} registros no tienen documento informado."
            )

        st.write("**Rol principal informado**")
        st.caption(
            "Se considera completo cuando el participante tiene un Rol principal cargado. "
            "Los registros sin este dato no pueden utilizarse completamente para analizar el perfil de los participantes."
        )

        if roles_faltantes == 0:
            st.success("Todos los registros tienen Rol principal informado.")
        else:
            st.warning(
                f"{roles_faltantes} registros no tienen Rol principal informado."
            )

        st.write("**Reinscripciones detectadas**")
        st.caption(
            "Una reinscripción ocurre cuando un mismo número de documento aparece en más de una inscripción. "
            "Puede corresponder a una persona que se registró más de una vez."
        )

        if reinscripciones == 0:
            st.info("No se detectaron reinscripciones.")
        else:
            st.info(
                f"Se detectaron {reinscripciones} reinscripciones adicionales. "
                "Para identificar participantes únicos se utiliza el número de documento."
            )

    with col2:
        st.write("**Mail válido**")
        st.caption(
            "Se considera válido cuando el correo tiene un formato correcto, por ejemplo nombre@dominio.com. "
            "Los correos vacíos o con formato incorrecto se consideran inválidos."
        )

        if mails_invalidos == 0:
            st.success("Todos los registros tienen un mail con formato válido.")
        else:
            st.warning(
                f"{mails_invalidos} registros tienen un mail con formato inválido."
            )

        st.write("**Tipo de inscripción informado**")
        st.caption(
            "Se considera completo cuando el registro tiene cargado el Tipo de inscripción. "
            "Los registros sin este dato no pueden utilizarse completamente para analizar los tipos de inscripción de la jornada."
        )

        if tipos_inscripcion_faltantes == 0:
            st.success(
                "Todos los registros tienen Tipo de inscripción informado."
            )
        else:
            st.warning(
                f"{tipos_inscripcion_faltantes} registros no tienen "
                "Tipo de inscripción informado."
            )

        st.write("**Filas completamente duplicadas**")
        st.caption(
            "Se considera duplicada una fila cuando todos sus valores son exactamente iguales a los de otra fila. "
            "Esto es diferente de una reinscripción, donde una misma persona puede tener registros distintos."
        )

        if filas_duplicadas == 0:
            st.success("No se detectaron filas completamente duplicadas.")
        else:
            st.warning(
                f"Se detectaron {filas_duplicadas} filas completamente duplicadas."
            )

    with col3:
        st.write("**Mail de bienvenida enviado**")
        st.caption(
            "Indica si consta el envío del correo de bienvenida al participante. "
            "Los registros donde no se realizó el envío permiten detectar posibles problemas en este proceso."
        )

        if welcome_mail_no_enviado == 0:
            st.success(
                "El mail de bienvenida fue enviado en todos los registros."
            )
        else:
            st.warning(
                f"{welcome_mail_no_enviado} registros no tienen "
                "mail de bienvenida enviado."
            )

        st.write("**Asistencia consistente**")
        st.caption(
            "Se compara el valor en la columna isPresent con la asistencia registrada por día. "
            "Se considera consistente cuando ambos indican el mismo resultado de asistencia."
        )

        if inconsistencias_asistencia == 0:
            st.success(
                "La asistencia es consistente en todos los registros."
            )
        else:
            st.warning(
                f"{inconsistencias_asistencia} registros presentan diferencias entre "
                "isPresent y la asistencia registrada por día."
            )