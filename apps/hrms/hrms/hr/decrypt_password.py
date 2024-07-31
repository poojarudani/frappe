import frappe
from frappe.utils.password import decrypt

def get_decrypted_user_password(user):
    auth = frappe.db.sql('''
        SELECT `password` FROM `__Auth`
        WHERE doctype=%s AND name=%s AND fieldname=%s
    ''', ('User', user, 'password'))

    if auth and auth[0][0]:
        return decrypt(auth[0][0])
    else:
        frappe.throw('Password not found', frappe.AuthenticationError)
