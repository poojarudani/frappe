# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class PorcentajeFactura(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		curso: DF.Link | None
		expediente: DF.Link
		importe: DF.Currency
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		plan: DF.Link | None
		porcentaje: DF.Percent
	# end: auto-generated types
	pass
