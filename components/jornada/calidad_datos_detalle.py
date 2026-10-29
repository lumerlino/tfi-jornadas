import streamlit as st


def mostrar_detalle_validaciones(df, datos):
    mascaras = datos["mascaras"]
    documentos_faltantes = datos["documentos_faltantes"]
    mails_invalidos = datos["mails_invalidos"]
    roles_faltantes = datos["roles_faltantes"]
    tipo_inscripcion_informado = datos["tipo_inscripcion_informado"]
    tipos_inscripcion_faltantes = datos["tipos_inscripcion_faltantes"]
    rol_informado = datos["rol_informado"]
    welcome_mail_no_enviado = datos["welcome_mail_no_enviado"]
    inconsistencias_asistencia = datos["inconsistencias_asistencia"]
    filas_duplicadas = datos["filas_duplicadas"]
    documentos_duplicados = datos["documentos_duplicados"]
    participantes_reinscriptos = datos["participantes_reinscriptos"]
    distribucion_reinscripciones = datos["distribucion_reinscripciones"]

    with st.expander("Ver detalle de las validaciones"):

        if documentos_faltantes > 0:
            st.markdown("##### Documentos faltantes")

            st.write(
                "Se consideran problemáticos los registros sin número de documento, "
                "porque el documento se utiliza para identificar participantes únicos."
            )

            st.warning(
                f"Se detectaron {documentos_faltantes} registros sin documento."
            )

            st.dataframe(
                df[
                    ~mascaras["documento_valido"]
                ][
                    [
                        "Nombre/s",
                        "Apellido/s",
                        "mail"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            st.divider()

        if mails_invalidos > 0:
            st.markdown("##### Mails con formato inválido")

            st.write(
                "Se consideran inválidos los correos vacíos o que no cumplen "
                "con el formato esperado de una dirección de email."
            )

            st.warning(
                f"Se detectaron {mails_invalidos} registros con un mail inválido."
            )

            st.dataframe(
                df[
                    ~mascaras["mail_valido"]
                ][
                    [
                        "documento",
                        "Nombre/s",
                        "Apellido/s",
                        "mail"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            st.divider()

        if roles_faltantes > 0:
            st.markdown("##### Rol principal no informado")

            st.write(
                "Se considera incompleto un registro cuando no tiene informado "
                "el Rol principal del participante."
            )

            st.warning(
                f"Se detectaron {roles_faltantes} registros sin Rol principal."
            )

            st.dataframe(
                df[
                    ~rol_informado
                ][
                    [
                        "documento",
                        "Nombre/s",
                        "Apellido/s",
                        "Rol principal"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            st.divider()

        if tipos_inscripcion_faltantes > 0:
            st.markdown("##### Tipo de inscripción no informado")

            st.write(
                "Se considera incompleto un registro cuando no tiene informado "
                "el tipo de inscripción."
            )

            st.warning(
                f"Se detectaron {tipos_inscripcion_faltantes} registros "
                "sin tipo de inscripción."
            )

            st.dataframe(
                df[
                    ~tipo_inscripcion_informado
                ][
                    [
                        "documento",
                        "Nombre/s",
                        "Apellido/s",
                        "Tipo inscripción"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            st.divider()

        if welcome_mail_no_enviado > 0:
            st.markdown("##### Mail de bienvenida no enviado")

            st.write(
                "Se muestran los registros donde no consta el envío "
                "del correo de bienvenida."
            )

            st.warning(
                f"Se detectaron {welcome_mail_no_enviado} registros "
                "sin mail de bienvenida enviado."
            )

            st.divider()

        if inconsistencias_asistencia > 0:
            st.markdown("##### Inconsistencias de asistencia")

            st.write(
                "Se compara la asistencia general informada en el archivo "
                "con la asistencia registrada por día. "
                "Se considera inconsistente cuando ambas no coinciden."
            )

            st.warning(
                f"Se detectaron {inconsistencias_asistencia} registros "
                "con diferencias de asistencia."
            )

            st.dataframe(
                df[
                    ~mascaras["asistencia_coherente"]
                ][
                    [
                        "documento",
                        "Nombre/s",
                        "Apellido/s",
                        "isPresent_original",
                        "asistio"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

            st.divider()

        if filas_duplicadas > 0:
            st.markdown("##### Filas completamente duplicadas")

            st.write(
                "Se consideran duplicadas las filas cuyos valores son "
                "exactamente iguales en todas sus columnas."
            )

            st.warning(
                f"Se detectaron {filas_duplicadas} filas completamente duplicadas."
            )

            st.divider()

        if documentos_duplicados > 0:
            st.markdown("##### Reinscripciones detectadas")

            st.write(
                f"Se detectaron **{participantes_reinscriptos} participantes** "
                f"con más de una inscripción."
            )

            detalle_distribucion = []

            for (
                cantidad_inscripciones,
                cantidad_participantes
            ) in distribucion_reinscripciones.items():

                texto_participantes = (
                    "participante"
                    if cantidad_participantes == 1
                    else "participantes"
                )

                texto_inscripciones = (
                    "inscripción"
                    if cantidad_inscripciones == 1
                    else "inscripciones"
                )

                detalle_distribucion.append(
                    f"{cantidad_participantes} "
                    f"{texto_participantes} con "
                    f"{cantidad_inscripciones} "
                    f"{texto_inscripciones}"
                )

            if detalle_distribucion:
                st.caption(
                    "Distribución: "
                    + "; ".join(detalle_distribucion)
                    + "."
                )

            st.dataframe(
                df[
                    ~mascaras["documento_unico"]
                ]
                .sort_values("documento")
                [
                    [
                        "documento",
                        "Nombre/s",
                        "Apellido/s",
                        "mail"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )