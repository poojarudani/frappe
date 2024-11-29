import frappe

def rename_courses_in_batches():
    # Configuración de lote
    batch_size = 100
    log_every = 10
    batch_count = 0
    log_body = ""

    # Obtener todas las entradas de Course
    courses = frappe.get_all(
        "Course",
        fields=["name", "plan_type", "abreviatura_categoria", "year", "code", "group"]
    )

    # Procesar en lotes
    for idx, course in enumerate(courses):
        if course.plan_type and course.abreviatura_categoria and course.year and course.code:
            # Generar el nombre base
            new_name = f"AF-{course.plan_type}-{course.abreviatura_categoria}-{course.year}-{course.code}"

            # Verificar si el nombre ya existe
            if frappe.db.exists("Course", new_name):
                # Agregar sufijo con el número de grupo
                new_name = f"{new_name}-{course.group}"

            try:
                # Renombrar el documento
                frappe.rename_doc("Course", course.name, new_name, force=True, merge=False)

                # Agregar al log
                log_body += f"Renamed: {course.name} → {new_name}\n"

            except Exception as e:
                # Registrar errores en el log
                log_body += f"Failed to rename: {course.name}\nError: {str(e)}\n\n"
        else:
            # Registrar entradas omitidas
            log_body += f"Skipped (Incomplete Fields): {course.name}\n"
            log_body += f"  plan_type: {course.plan_type or 'None'}\n"
            log_body += f"  abreviatura_categoria: {course.abreviatura_categoria or 'None'}\n"
            log_body += f"  year: {course.year or 'None'}\n"
            log_body += f"  code: {course.code or 'None'}\n"
            log_body += f"  group: {course.group or 'None'}\n\n"

        # Controlar el tamaño del lote
        if (idx + 1) % batch_size == 0:
            batch_count += 1

            # Registrar log cada 10 lotes
            if batch_count % log_every == 0:
                frappe.log_error(
                    title=f"Batch {batch_count}: Course Renaming Log",
                    message=log_body
                )
                # Reiniciar el log_body después de registrarlo
                log_body = ""

    # Registrar log final si hay datos pendientes
    if log_body:
        frappe.log_error(title="Final Batch: Course Renaming Log", message=log_body)
