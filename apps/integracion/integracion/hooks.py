app_name = "integracion"
app_title = "Integracion"
app_publisher = "Xappiens"
app_description = "Integracion"
app_email = "info@xappiens.com"
app_license = "mit"

# Hooks for DocType events
doc_events = {
    "User": {
        "on_update": "integracion.integracion.password_utils.create_user_in_crm",
        "on_trash": "integracion.integracion.delete_user_crm.delete_user_in_crm",
        "before_validate": "integracion.integracion.not_set_over.force_disable_user"
    },
    "__Auth": {
        "on_update": "integracion.integracion.password_update.update_password_in_crm"
    },
    "File": {
        "on_create" : "integracion.integracion.subir_archivo_sp.on_update_or_create",
        "on_update" : "integracion.integracion.subir_archivo_sp.on_update_or_create"
    },
    "Purchase Invoice": {
        "before_save": "integracion.integracion.subir_archivo_sp.handle_structure_change"
    },
    "Sales Invoice": {
        "before_save": "integracion.integracion.subir_archivo_sp.handle_structure_change",
        "after_insert": "integracion.integracion.metodos_varios.copy_attachments_from_sales_order"
    },
    "Course": {
        "on_trash": "integracion.integracion.courses_overrides.delete_course_link"
    },
    "ToDo":{
        "after_insert": "integracion.integracion.metodos_varios.notify_on_assign"
    },
    "Course": {
        "after_insert": "integracion.integracion.courses_overrides.send_course_to_crm"
    },
    "Project": {
        "after_insert": "integracion.integracion.subir_archivo_sp.create_project_folder"
    },
    "Task": {
        "on_update": "integracion.integracion.task_update.update_activity_state"
    },
    "Modificaciones RRHH": {
        "on_submit": "integracion.integracion.renombrar_hoja.update_job_offer_and_employee"
    }
}

override_whitelisted_methods = {
    "integracion.create_purchase_invoice": "integracion.integracion.create_purchase_invoice.create_purchase_invoice",
    "integracion.integracion.employee_link_override.filter_employees": "integracion.integracion.employee_link_override.filter_employees",
    "integracion.integracion.subir_archivo_sp.get_sharepoint_structure" : "integracion.integracion.subir_archivo_sp.get_sharepoint_structure",
    "integracion.integracion.generate_c34_compra": "integracion.integracion.generate_c34_compra.generate_c34_compra",
    "integracion.integracion.generate_c34_venta": "integracion.integracion.generate_c34_venta.generate_c34_venta",
    "integracion.integracion.sii.sii_integracion.enviar_facturas_emitidas_wrapper": "integracion.integracion.sii.sii_integracion.enviar_facturas_emitidas_wrapper",
    "integracion.integracion.sii.sii_integracion.enviar_facturas_recibidas_wrapper": "integracion.integracion.sii.sii_integracion.enviar_facturas_recibidas_wrapper",
    "education.education.doctype.course.course.add_course_to_programs": "integracion.integracion.sii.sii_integracion.custom_add_course_to_programs",
    "education.education.doctype.course.course.get_programs_without_course": "integracion.integracion.sii.sii_integracion.custom_get_programs_without_course",
    "integracion.integracion.custom_pdf_make.custom_download_and_attach_pdf": "integracion.integracion.custom_pdf_make.custom_download_and_attach_pdf",
    "integracion.invoice_from_email": "integracion.integracion.invoice_from_email.invoice_from_email",
    "integracion.make_employee": "integracion.integracion.make_employee.make_employee",
    "integracion.subir_nominas": "integracion.integracion.subir_nominas.subir_nominas",
    "integracion.import_journal_entries": "integracion.integracion.import_journal_entries.import_journal_entries",
    "hrms.hr.doctype.employee_onboarding.employee_onboarding.make_employee": "integracion.integracion.employee_onboarding_overr.make_employee",
    "integracion.chage_state_to_baja": "integracion.integracion.renombrar_hoja.change_state_to_baja",
    "integracion.export_expense_claim_summary": "integracion.integracion.export_excel.export_expense_claim_summary",
    "integracion.get_reconciled_transaction_count": "integracion.integracion.number_card_scripts.get_reconciled_transaction_count",
    "integracion.get_prom_reconciled_transaction": "integracion.integracion.number_card_scripts.get_prom_reconciled_transaction"

    #"erpnext.accounts.doctype.bank_transaction.bank_transaction.reconcile_vouchers": "integracion.integracion.bank_tool_over.reconcile_vouchers"

    #"erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice": "integracion.integracion.metodos_varios.make_sales_invoice",

}

permission_query_conditions = {
    "Job Offer": "integracion.integracion.permissions.job_offer_query",
    "User": "integracion.integracion.permissions.user_query",
    "Project": "integracion.integracion.permissions.project_query",
    "Attendance": "integracion.integracion.permissions.attendance_query",
    #"Course": "integracion.integracion.permissions.course_query"
}


override_doctype_class = {
    "Purchase Invoice": "integracion.integracion.purchase_invoice_override.CustomPurchaseInvoice",
    "Job Offer": "integracion.integracion.job_offer_override.CustomJobOffer",
    "Opportunity": "integracion.integracion.opportunity_override.CustomOpportunity",
    "Student": "integracion.integracion.student_override.CustomStudent",
    "Employee Onboarding": "integracion.integracion.employee_onboarding_overr.CustomEmployeeOnboarding",
    "Employee Onboarding Controller": "integracion.integracion.empl_onb_con_over.CustomEmployeeBoardingController",
    "Program Enrollment": "integracion.integracion.program_override.CustomProgramEnrollment",
    "Bank Statement Import": "integracion.integracion.bank_tool_over.CustomBankStatementImport",
    "Account": "integracion.integracion.account_override.CustomAccount",
    "Assignment Rule": "integracion.integracion.assignament_override.AssignmentRuleOverride",
    "Employee Separation" : "integracion.integracion.employee_sep_over.CustomEmployeeSeparation",

}

override_doctype_dashboards = {
   "Planes Formativos": "integracion.integracion.planes_formativos_dashboard.get_data"
}


scheduler_events = {
    "cron": {
        "0 16 * * *":[
            #"integracion.integracion.hc_diary_noti.enviar_notificacion_a_asesoria"
        ],
        
    },
    "daily": [
        "integracion.integracion.employee_status_update.check_contract_end"
        "integracion.integracion.employee_status_update.update_employee_status",
        "integracion.integracion.employee_status_update.disable_inactive_employee_users"
]
}

# Añadir el enlace de Font Awesome al encabezado de HTML
app_include_css = [
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
    "/assets/integracion/css/custom_styles.css"
]

app_include_js = [
    "/assets/integracion/js/custom_printview.js",
    "/assets/integracion/js/custom_communication.js",
    "/assets/integracion/js/custom_buttonsactu.js",
    "/assets/integracion/js/custom_notify.js",
    "/assets/integracion/js/custom_genlibmyr.js",
    "/assets/integracion/js/custom_balanceshote.js",
    "/assets/integracion/js/custom_profit_and_loss_statement.js",
    "/assets/integracion/js/custom_mte_attendance.js",
    "/assets/integracion/js/custom_indicator.js"
]

page_js = {
    "user-profile": "public/js/custom_user_p.js"
}




doctype_js = {
    "Opportunity": "public/js/custom_opportunity.js",
    "Program Enrollment": "public/js/program_enrollment.js",
    "Student Applicant": "public/js/student_applicant.js",
}


# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/integracion/css/integracion.css"
# app_include_js = "/assets/integracion/js/integracion.js"

# include js, css files in header of web template
# web_include_css = "/assets/integracion/css/integracion.css"
# web_include_js = "/assets/integracion/js/integracion.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "integracion/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "integracion/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "integracion.utils.jinja_methods",
# 	"filters": "integracion.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "integracion.install.before_install"
# after_install = "integracion.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "integracion.uninstall.before_uninstall"
# after_uninstall = "integracion.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "integracion.utils.before_app_install"
# after_app_install = "integracion.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "integracion.utils.before_app_uninstall"
# after_app_uninstall = "integracion.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "integracion.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"integracion.tasks.all"
# 	],
# 	"daily": [
# 		"integracion.tasks.daily"
# 	],
# 	"hourly": [
# 		"integracion.tasks.hourly"
# 	],
# 	"weekly": [
# 		"integracion.tasks.weekly"
# 	],
# 	"monthly": [
# 		"integracion.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "integracion.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "integracion.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "integracion.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["integracion.utils.before_request"]
# after_request = ["integracion.utils.after_request"]

# Job Events
# ----------
# before_job = ["integracion.utils.before_job"]
# after_job = ["integracion.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"integracion.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

