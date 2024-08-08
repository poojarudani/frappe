from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice
import frappe

class CustomPurchaseInvoice(PurchaseInvoice):
    # Añadir un atributo para control de sobrescritura
    allow_external_status_change = False

    def set_status(self, update=False, status=None, update_modified=True):
        # Lógica original de la clase base
        super().set_status(update=update, status=status, update_modified=update_modified)

        # Permitir cambios externos al estado si se habilitó
        if self.allow_external_status_change:
            frappe.log_error(f"External change allowed for document: {self.name}", "External Status Change")
            return

        # Lógica adicional para el estado personalizado
        if self.docstatus == 0:  # Estado Borrador
            # Comprobar si se ha aprobado para pago pero no está en "Remesa Emitida"
            if self.custom_aprobado_para_pago and self.status != "Remesa Emitida":
                if self.status != "Aprobada para pago":
                    self.status = "Aprobada para pago"
                    self.db_set('status', self.status, update_modified=update_modified)
            
            # Comprobar si debe cambiarse a "Remesa Emitida"
            if self.custom_remesa_emitida and self.status == "Aprobada para pago":
                self.status = "Remesa Emitida"
                self.db_set('status', self.status, update_modified=update_modified)
