# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CellularLines(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		empleado: DF.Link | None
		numero: DF.Data | None
		numero_corto: DF.Data | None
		tipo_linea: DF.Literal["Voz", "Datos", "Centralita"]
	# end: auto-generated types
	pass
