import os
import json
import logging
import datetime
from urllib.parse import quote
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from lxml import etree
from bs4 import BeautifulSoup  # Librería para manejar HTML
import frappe
from frappe import _

# Leer credenciales desde el archivo de configuración del sitio
site_config = frappe.get_site_config()
user_email = site_config.get('user_sp')
user_password = site_config.get('pass_sp')
sharepoint_base_url = "https://grupoatu365.sharepoint.com/sites/DepartamentodeAdministracin2-Contabilidad/Shared%20Documents/Contabilidad/Cuaderno34%20-%20Facturas%20de%20Compra"

# Configurar el logger
logger = logging.getLogger(__name__)
handler = logging.FileHandler('/home/frappe/frappe-bench/apps/integracion/integracion/integracion/logs/generate_c34.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

@frappe.whitelist()
def generate_c34(selected_invoices):
    logger.info("Inicio de la generación de Cuaderno 34")
    selected_invoices = frappe.parse_json(selected_invoices)
    invoices_by_company = {}

    # Agrupar facturas por empresa
    for invoice_id in selected_invoices:
        try:
            invoice = frappe.get_doc("Purchase Invoice", invoice_id)
            company = invoice.company
            if company not in invoices_by_company:
                invoices_by_company[company] = []
            invoices_by_company[company].append(invoice)
            logger.debug(f"Factura {invoice_id} agregada a la empresa {company}")
        except Exception as e:
            logger.error(f"Error al obtener la factura {invoice_id}: {e}")

    files = []
    for company, invoices in invoices_by_company.items():
        try:
            abbr = frappe.get_value("Company", company, "abbr")
            now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            fichero_id_value = f"C34-{abbr}-{now}"
            
            # Crear el elemento principal del XML conforme al estándar SEPA
            root = etree.Element("Document", xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03")
            cstmr_cdt_trf_initn = etree.SubElement(root, "CstmrCdtTrfInitn")

            # Crear el header del grupo
            grp_hdr = etree.SubElement(cstmr_cdt_trf_initn, "GrpHdr")
            msg_id = etree.SubElement(grp_hdr, "MsgId")
            msg_id.text = fichero_id_value
            cre_dt_tm = etree.SubElement(grp_hdr, "CreDtTm")
            cre_dt_tm.text = now
            nb_of_txs = etree.SubElement(grp_hdr, "NbOfTxs")
            nb_of_txs.text = str(len(invoices))
            ctrl_sum = etree.SubElement(grp_hdr, "CtrlSum")
            ctrl_sum.text = str(sum(invoice.grand_total for invoice in invoices))
            initg_pty = etree.SubElement(grp_hdr, "InitgPty")
            nm = etree.SubElement(initg_pty, "Nm")
            nm.text = company
            id_elem = etree.SubElement(initg_pty, "Id")
            org_id = etree.SubElement(id_elem, "OrgId")
            othr = etree.SubElement(org_id, "Othr")
            othr_id = etree.SubElement(othr, "Id")
            othr_id.text = frappe.get_value("Company", company, "tax_id")

            # Información de pago
            pmt_inf = etree.SubElement(cstmr_cdt_trf_initn, "PmtInf")
            pmt_inf_id = etree.SubElement(pmt_inf, "PmtInfId")
            pmt_inf_id.text = f"PMT-{abbr}-{now}"
            pmt_mtd = etree.SubElement(pmt_inf, "PmtMtd")
            pmt_mtd.text = "TRF"
            btch_bookg = etree.SubElement(pmt_inf, "BtchBookg")
            btch_bookg.text = "false"
            nb_of_txs_pmt_inf = etree.SubElement(pmt_inf, "NbOfTxs")
            nb_of_txs_pmt_inf.text = str(len(invoices))
            ctrl_sum_pmt_inf = etree.SubElement(pmt_inf, "CtrlSum")
            ctrl_sum_pmt_inf.text = str(sum(invoice.grand_total for invoice in invoices))
            pmt_tp_inf = etree.SubElement(pmt_inf, "PmtTpInf")
            instr_prty = etree.SubElement(pmt_tp_inf, "InstrPrty")
            instr_prty.text = "NORM"
            svc_lvl = etree.SubElement(pmt_tp_inf, "SvcLvl")
            svc_lvl_cd = etree.SubElement(svc_lvl, "Cd")
            svc_lvl_cd.text = "SEPA"
            reqd_exctn_dt = etree.SubElement(pmt_inf, "ReqdExctnDt")
            reqd_exctn_dt.text = frappe.utils.nowdate()

            # Ordenante
            dbtr = etree.SubElement(pmt_inf, "Dbtr")
            dbtr_nm = etree.SubElement(dbtr, "Nm")
            dbtr_nm.text = company

            # Extraer el texto plano del campo HTML address_html
            #address_html = frappe.get_value("Company", company, "address_html")
            #soup = BeautifulSoup(address_html, 'html.parser')
            #address_text = soup.get_text(separator=", ")

            dbtr_pstl_adr = etree.SubElement(dbtr, "PstlAdr")
            dbtr_ctry = etree.SubElement(dbtr_pstl_adr, "Ctry")
            dbtr_ctry.text = "ES"
            dbtr_adr_line = etree.SubElement(dbtr_pstl_adr, "AdrLine")
            #dbtr_adr_line.text = address_text
            dbtr_adr_line.text = "address_text"
            dbtr_id = etree.SubElement(dbtr, "Id")
            dbtr_org_id = etree.SubElement(dbtr_id, "OrgId")
            dbtr_othr = etree.SubElement(dbtr_org_id, "Othr")
            dbtr_othr_id = etree.SubElement(dbtr_othr, "Id")
            dbtr_othr_id.text = frappe.get_value("Company", company, "tax_id")
            dbtr_acct = etree.SubElement(pmt_inf, "DbtrAcct")
            dbtr_acct_id = etree.SubElement(dbtr_acct, "Id")
            dbtr_acct_iban = etree.SubElement(dbtr_acct_id, "IBAN")
            dbtr_acct_iban.text = frappe.get_value("Company", company, "default_bank_account")
            dbtr_agt = etree.SubElement(pmt_inf, "DbtrAgt")
            dbtr_fin_instn_id = etree.SubElement(dbtr_agt, "FinInstnId")

            for invoice in invoices:
                try:
                    cdt_trf_tx_inf = etree.SubElement(pmt_inf, "CdtTrfTxInf")
                    pmt_id = etree.SubElement(cdt_trf_tx_inf, "PmtId")
                    instr_id = etree.SubElement(pmt_id, "InstrId")
                    instr_id.text = invoice.name
                    end_to_end_id = etree.SubElement(pmt_id, "EndToEndId")
                    end_to_end_id.text = invoice.name
                    amt = etree.SubElement(cdt_trf_tx_inf, "Amt")
                    instd_amt = etree.SubElement(amt, "InstdAmt", Ccy="EUR")
                    instd_amt.text = str(invoice.grand_total)
                    cdtr_agt = etree.SubElement(cdt_trf_tx_inf, "CdtrAgt")
                    cdtr_fin_instn_id = etree.SubElement(cdtr_agt, "FinInstnId")
                    cdtr_bic = etree.SubElement(cdtr_fin_instn_id, "BIC")
                    cdtr_bic.text = frappe.get_value("Supplier", invoice.supplier, "bic")
                    cdtr = etree.SubElement(cdt_trf_tx_inf, "Cdtr")
                    cdtr_nm = etree.SubElement(cdtr, "Nm")
                    cdtr_nm.text = invoice.supplier_name
                    cdtr_acct = etree.SubElement(cdt_trf_tx_inf, "CdtrAcct")
                    cdtr_acct_id = etree.SubElement(cdtr_acct, "Id")
                    cdtr_acct_iban = etree.SubElement(cdtr_acct_id, "IBAN")
                    cdtr_acct_iban.text = frappe.get_value("Supplier", invoice.supplier, "default_bank_account")
                    rmt_inf = etree.SubElement(cdt_trf_tx_inf, "RmtInf")
                    ustrd = etree.SubElement(rmt_inf, "Ustrd")
                    ustrd.text = invoice.remarks or "Pago de factura"

                    logger.debug(f"Pago añadido para la factura {invoice.name} del proveedor {invoice.supplier_name}")
                except Exception as e:
                    logger.error(f"Error al procesar la factura {invoice.name}: {e}")

            xml_data = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")
            file_path = f"/home/frappe/frappe-bench/sites/erp.grupoatu.com/private/cuaderno/{fichero_id_value}.xml"
            with open(file_path, "wb") as f:
                f.write(xml_data)
            files.append((file_path, company, fichero_id_value))
            logger.info(f"Archivo Cuaderno 34 generado para {company}: {file_path}")

        except Exception as e:
            logger.error(f"Error al generar Cuaderno 34 para {company}: {e}")

    sharepoint_urls = []
    for file_path, company, fichero_id_value in files:
        try:
            sharepoint_url = upload_file_to_sharepoint(file_path, company, fichero_id_value)
            sharepoint_urls.append(sharepoint_url)
            # Eliminar el archivo local después de subirlo a SharePoint
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Archivo local {file_path} eliminado después de subirlo a SharePoint")
        except Exception as e:
            logger.error(f"Error al subir el archivo {file_path} a SharePoint: {e}")

    return sharepoint_urls

def create_folder_if_not_exists(ctx, folder_relative_url, folder_name):
    try:
        logger.info(f"Comprobando existencia de carpeta en la ruta: /{folder_relative_url}/{folder_name}")
        parent_folder = ctx.web.get_folder_by_server_relative_url(f"{folder_relative_url}")
        ctx.load(parent_folder)
        ctx.execute_query()
        logger.info(f"Conectado a parent {parent_folder}")

        folders = parent_folder.folders
        ctx.load(folders)
        ctx.execute_query()

        folder_names = [folder.properties['Name'] for folder in folders]

        if folder_name in folder_names:
            logger.info(f"La carpeta ya existe: {folder_relative_url}/{folder_name}")
        else:
            new_folder = parent_folder.folders.add(folder_name).execute_query()
            logger.info(f"Carpeta creada: {new_folder.serverRelativeUrl}")
    except Exception as e:
        logger.error(f"Error verificando/creando carpeta en {folder_relative_url}/{folder_name}: {e}")
        raise

def upload_file_to_sharepoint(file_path, company, fichero_id_value):
    logger.info(f"Subiendo archivo {file_path} a SharePoint para la compañía {company} con Cuaderno {fichero_id_value}")
    try:
        if not file_path or not os.path.isfile(file_path):
            logger.error(f"El archivo no existe o no se proporcionó una ruta válida: {file_path}")
            return

        # Extraer la ruta relativa y el nombre del sitio desde la URL completa
        start_idx = sharepoint_base_url.find('/sites/')
        if start_idx == -1:
            logger.error("La URL no contiene '/sites/'. No se puede calcular la ruta relativa.")
            return
        site_url = sharepoint_base_url[:start_idx + len('/sites/') + sharepoint_base_url[start_idx + len('/sites/'):].find('/')]
        site_relative_url = sharepoint_base_url[start_idx:start_idx + len('/sites/') + sharepoint_base_url[start_idx + len('/sites/'):].find('/')]
        relative_path = sharepoint_base_url[start_idx + len(site_relative_url):].lstrip('/')
        logger.info(f"Ruta relativa calculada: {relative_path}")
        logger.info(f"Conectando al contexto del sitio: {site_url}")

        credentials = UserCredential(user_email, user_password)
        ctx = ClientContext(site_url).with_credentials(credentials)

        company_folder_name = quote(company)
        cuaderno_folder_name = quote(fichero_id_value)

        # Crear la carpeta de la compañía si no existe
        create_folder_if_not_exists(ctx, relative_path, company_folder_name)

        # Crear la carpeta del Cuaderno 34 dentro de la carpeta de la compañía
        company_folder_relative_url = f"{relative_path}/{company_folder_name}".strip('/')
        create_folder_if_not_exists(ctx, company_folder_relative_url, cuaderno_folder_name)

        with open(file_path, 'rb') as file_content:
            content = file_content.read()

        file_name = os.path.basename(file_path)
        file_url = f"{company_folder_relative_url}/{cuaderno_folder_name}/{file_name}"
        logger.info(f"Intentando subir archivo a: {file_url}")

        try:
            target_folder = ctx.web.get_folder_by_server_relative_url(f"{company_folder_relative_url}/{cuaderno_folder_name}")
            ctx.load(target_folder)
            ctx.execute_query()

            target_folder.upload_file(file_name, content).execute_query()
            logger.info(f"Archivo subido: {file_url}")

            # Devolver la URL de SharePoint
            sharepoint_url = f"{site_url}/{file_url}"
            return sharepoint_url

        except Exception as e:
            logger.error(f"Error al subir archivo a SharePoint: {str(e)}")
            return None
    except Exception as e:
        logger.error(f"Error al subir archivo a SharePoint: {str(e)}")
        return None