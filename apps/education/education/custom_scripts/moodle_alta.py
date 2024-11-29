import random
import string
import requests
import time
import frappe
from frappe import _

@frappe.whitelist()
def generar_contrasena_aleatoria(length=4):
    """Genera una contraseña aleatoria de 4 dígitos."""
    return ''.join(random.choice(string.digits) for _ in range(length))


@frappe.whitelist()
def sync_students_to_moodle(course_name):
    """
    Sincroniza estudiantes con Moodle, los agrega al curso y los incluye en el grupo especificado.
    - Verifica si el grupo ya existe antes de intentar crearlo.
    - Crea usuarios si no existen y los agrega al curso y grupo.
    """
    log_steps = []

    try:
        # Obtener el documento del curso
        course_doc = frappe.get_doc("Course", course_name)
        log_steps.append(f"Curso obtenido:\nNombre: {course_doc.name}\nCódigo Moodle: {course_doc.moodle_course_code}\nGrupo: {course_doc.group}")

        # Configuración de Moodle
        moodle_instance = frappe.get_doc("Moodle Instance", course_doc.virtual_class)
        moodle_url = moodle_instance.site_url
        if not moodle_url.startswith("http://") and not moodle_url.startswith("https://"):
            moodle_url = f"https://{moodle_url}"
        api_url = f"{moodle_url}/webservice/rest/server.php"
        moodle_token = moodle_instance.api_key
        log_steps.append(f"Instancia de Moodle configurada:\nNombre: {moodle_instance.site_name}\nURL: {moodle_url}")

        ########################################################################################################################

        # Verificar si el grupo ya existe en Moodle
        group_id = None
        group_params = {
            "wstoken": moodle_token,
            "wsfunction": "core_group_get_course_groups",
            "moodlewsrestformat": "json",
            "courseid": course_doc.moodle_course_code
        }
        group_response = requests.get(api_url, params=group_params)
        group_data = group_response.json()
        log_steps.append(f"Respuesta completa de grupos en Moodle:\n{group_data}")

        if isinstance(group_data, list):
            for group in group_data:
                if group["name"] == course_doc.group:
                    group_id = group["id"]
                    log_steps.append(f"Grupo ya existente en Moodle:\nNombre: {course_doc.group}\nID: {group_id}")
                    break

        # Crear el grupo solo si no existe
        if not group_id:
            try:
                create_group_params = {
                    "wstoken": moodle_token,
                    "wsfunction": "core_group_create_groups",
                    "moodlewsrestformat": "json",
                    "groups[0][name]": course_doc.group,
                    "groups[0][courseid]": course_doc.moodle_course_code,
                    "groups[0][description]": f"Grupo para el curso {course_doc.name}"
                }
                create_group_response = requests.post(api_url, data=create_group_params)
                create_group_data = create_group_response.json()

                if isinstance(create_group_data, list):
                    for group in create_group_data:
                        if group.get("id"):
                            group_id = group["id"]
                            log_steps.append(f"Grupo creado en Moodle:\nNombre: {course_doc.group}\nID: {group_id}")
                            break
                elif "errorcode" in create_group_data and create_group_data["errorcode"] == "invalidparameter":
                    # Si Moodle indica que ya existe, loguearlo y continuar
                    log_steps.append(f"Grupo ya existe según Moodle, pero no fue detectado inicialmente:\n{create_group_data}")
                else:
                    log_steps.append(f"Error al crear el grupo en Moodle:\nRespuesta: {create_group_data}")
                    frappe.log_error("\n".join(log_steps), f"Error en Sincronización de Curso: {course_doc.name}")
                    return "Error al crear el grupo en Moodle."
            except Exception as group_creation_error:
                log_steps.append(f"Excepción al crear grupo: {str(group_creation_error)}")
                frappe.log_error("\n".join(log_steps), f"Error en Sincronización de Curso: {course_doc.name}")
                return "Error crítico al intentar crear el grupo en Moodle."


        ########################################################################################################################


        # Obtener estudiantes habilitados
        student_ids = [entry.estudiante for entry in course_doc.custom_estudiantes if entry.estudiante]
        enabled_students = frappe.get_all(
            "Student",
            filters={"name": ["in", student_ids], "enabled": 1},
            fields=["name", "first_name", "last_name", "dni", "student_mobile_number", "student_email_id"]
        )
        log_steps.append(f"Estudiantes habilitados:\n{enabled_students}")

        # Procesar estudiantes
        for student_data in enabled_students:
            try:
                dni = student_data["dni"]
                log_steps.append(f"\nProcesando estudiante:\nDNI: {dni}\nNombre: {student_data['first_name']} {student_data['last_name']}")

                # Verificar si el usuario ya existe en Moodle
                check_user_params = {
                    "wstoken": moodle_token,
                    "wsfunction": "core_user_get_users",
                    "moodlewsrestformat": "json",
                    "criteria[0][key]": "username",
                    "criteria[0][value]": dni.lower()  # El DNI como username
                }
                response = requests.get(api_url, params=check_user_params)
                response_data = response.json()

                if response_data.get("users"):
                    user_id = response_data["users"][0]["id"]
                    log_steps.append(f"Usuario ya existente en Moodle:\nID Moodle: {user_id}")
                else:
                    # Crear nuevo usuario con contraseña obligatoria
                    create_user_params = {
                        "wstoken": moodle_token,
                        "wsfunction": "core_user_create_users",
                        "moodlewsrestformat": "json",
                        "users[0][username]": dni.lower(),
                        "users[0][firstname]": student_data["first_name"],
                        "users[0][lastname]": student_data["last_name"],
                        "users[0][email]": student_data["student_email_id"],
                        "users[0][phone1]": student_data["student_mobile_number"],
                        "users[0][idnumber]": dni.lower(),
                        "users[0][password]": dni.lower(),  # Contraseña inicial igual al DNI
                        "users[0][preferences][0][type]": "auth_forcepasswordchange",  # Forzar cambio de contraseña
                        "users[0][preferences][0][value]": "1"
                    }
                    create_response = requests.post(api_url, data=create_user_params)
                    create_response_data = create_response.json()

                    if isinstance(create_response_data, list):
                        for user in create_response_data:
                            if user.get("id"):
                                user_id = user["id"]
                                log_steps.append(f"Usuario creado en Moodle:\nID Moodle: {user_id}")
                                
                                # Solicitar restablecimiento de contraseña
                                reset_password_params = {
                                    "wstoken": moodle_token,
                                    "wsfunction": "core_auth_request_password_reset",
                                    "moodlewsrestformat": "json",
                                    "username": dni.lower(),  # Usar el DNI como nombre de usuario
                                }
                                reset_response = requests.post(api_url, data=reset_password_params)
                                reset_response_data = reset_response.json()

                                if reset_response.status_code == 200:
                                    log_steps.append(f"Correo de restablecimiento de contraseña enviado a: {student_data['student_email_id']}")
                                else:
                                    log_steps.append(f"Error al enviar el correo de restablecimiento de contraseña:\n{reset_response_data}")
                            else:
                                log_steps.append(f"Error al crear usuario en Moodle: no se encontró un ID de usuario en la respuesta.\nDNI: {dni}\nRespuesta: {create_response_data}")
                    else:
                        log_steps.append(f"Error al crear usuario en Moodle: respuesta inesperada.\nDNI: {dni}\nRespuesta: {create_response_data}")

                timestart = int(time.mktime(course_doc.start_date.timetuple()))
                timeend = int(time.mktime(course_doc.end_date.timetuple()))
                # Vincular usuario al curso
                enroll_params = {
                    "wstoken": moodle_token,
                    "wsfunction": "enrol_manual_enrol_users",
                    "moodlewsrestformat": "json",
                    "enrolments[0][roleid]": 5,  # ID de rol para estudiante
                    "enrolments[0][userid]": user_id,
                    "enrolments[0][courseid]": course_doc.moodle_course_code,
                    "enrolments[0][timestart]": timestart,
                    "enrolments[0][timeend]": timeend,
                }
                enroll_response = requests.post(api_url, data=enroll_params)
                enroll_response_data = enroll_response.json()

                if enroll_response.status_code == 200:
                    log_steps.append(f"Usuario vinculado al curso:\nDNI: {dni}\nID Curso Moodle: {course_doc.moodle_course_code}")
                else:
                    log_steps.append(f"Error al vincular usuario al curso:\nDNI: {dni}\nRespuesta: {enroll_response_data}")

                # Vincular usuario al grupo
                add_to_group_params = {
                    "wstoken": moodle_token,
                    "wsfunction": "core_group_add_group_members",
                    "moodlewsrestformat": "json",
                    "members[0][groupid]": group_id,  # ID del grupo
                    "members[0][userid]": user_id    # ID del usuario
                }
                try:
                    add_to_group_response = requests.post(api_url, data=add_to_group_params)
                    add_to_group_data = add_to_group_response.json()
                except Exception as e:
                    log_steps.append(f"Error al agregar usuario al grupo: {str(e)}")
                    continue

                if add_to_group_response.status_code == 200:
                    log_steps.append(f"Usuario agregado al grupo:\nDNI: {dni}\nGrupo: {course_doc.group}")
                else:
                    log_steps.append(f"Error al agregar usuario al grupo:\nDNI: {dni}\nRespuesta: {add_to_group_data}")

            except Exception as student_error:
                log_steps.append(f"Error al procesar estudiante {student_data['name']} (DNI: {dni}): {str(student_error)}")
                continue

        log_steps.append("Sincronización completada con éxito.")

    except Exception as e:
        log_steps.append(f"Error general: {str(e)}")

    frappe.log_error("\n".join(log_steps), f"Sincronización de Curso: {course_doc.name}")
    return "Sincronización completada con éxito."



########################################################################################################################
########################################################################################################################
########################################################################################################################



@frappe.whitelist()
def send_credentials_to_new_users(course_name):
    """
    Simula el envío de credenciales a usuarios nuevos:
    - Detecta usuarios inscritos en el curso con auth_forcepasswordchange activado.
    - Registra los datos completos devueltos por Moodle en el log para diagnóstico.
    """
    log_steps = []

    try:
        # Obtener el documento del curso
        course_doc = frappe.get_doc("Course", course_name)
        log_steps.append(f"Curso obtenido:\nNombre: {course_doc.name}\nClase Virtual: {course_doc.virtual_class}")

        # Configuración de Moodle
        moodle_instance = frappe.get_doc("Moodle Instance", course_doc.virtual_class)
        moodle_name = moodle_instance.site_name
        moodle_url = moodle_instance.site_url
        if not moodle_url.startswith("http://") and not moodle_url.startswith("https://"):
            moodle_url = f"https://{moodle_url}"
        api_url = f"{moodle_url}/webservice/rest/server.php"
        moodle_token = moodle_instance.api_key
        log_steps.append(f"Instancia de Moodle configurada:\nNombre: {moodle_name}\nURL: {moodle_url}")

        # Obtener la plantilla de correo
        email_template = frappe.get_doc("Email Template", "alta_alumno_moodle")
        log_steps.append(f"Plantilla de correo obtenida:\nNombre: {email_template.name}\nAsunto: {email_template.subject}")

        # Buscar usuarios inscritos en el curso
        enrolled_users_params = {
            "wstoken": moodle_token,
            "wsfunction": "core_enrol_get_enrolled_users",
            "moodlewsrestformat": "json",
            "courseid": course_doc.moodle_course_code
        }
        enrolled_users_response = requests.get(api_url, params=enrolled_users_params)
        enrolled_users_data = enrolled_users_response.json()

        # Registrar la respuesta completa para diagnóstico
        log_steps.append(f"Respuesta completa de usuarios inscritos en el curso:\n{enrolled_users_data}")

        # Lista para usuarios detectados con auth_forcepasswordchange
        users_with_force_password_change = []

        if isinstance(enrolled_users_data, list):
            for user in enrolled_users_data:
                try:
                    # Verificar si auth_forcepasswordchange está activado
                    auth_forcepasswordchange = any(
                        pref["type"] == "auth_forcepasswordchange" and pref["value"] is True
                        for pref in user.get("preferences", [])
                    )
                    if auth_forcepasswordchange:
                        users_with_force_password_change.append({
                            "fullname": user["fullname"],
                            "email": user["email"],
                            "username": user["username"]
                        })

                        # Simulación: Registrar datos del correo preparado
                        data_to_send = {
                            "first_name": user["firstname"],
                            "username": user["username"],
                            "password": "ContraseñaGenerada",  # Simulación de contraseña
                            "moodle_name": moodle_name,
                            "moodle_url": moodle_url
                        }
                        email_content = frappe.render_template(email_template.response, data_to_send)
                        log_steps.append(f"Correo preparado para {user['email']}:\n{email_content}")
                    else:
                        log_steps.append(f"Usuario no requiere cambio de contraseña:\nNombre: {user['fullname']}\nEmail: {user['email']}")

                except Exception as user_error:
                    log_steps.append(f"Error al procesar usuario {user['fullname']} (Email: {user['email']}): {str(user_error)}")
                    continue

        # Registrar todos los usuarios detectados con auth_forcepasswordchange
        if users_with_force_password_change:
            log_steps.append(f"Usuarios con auth_forcepasswordchange activado:\n{users_with_force_password_change}")
        else:
            log_steps.append("No se encontraron usuarios con auth_forcepasswordchange activado.")

        log_steps.append("Simulación de envío de credenciales completada con éxito.")

    except Exception as e:
        log_steps.append(f"Error general: {str(e)}")

    # Registrar log con el nombre del curso en el título
    log_title = f"Diagnóstico de Envío de Credenciales: {course_doc.name}"
    frappe.log_error("\n".join(log_steps), log_title)
    return "Diagnóstico completado con éxito."
