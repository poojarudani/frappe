from zeep import Client
from lxml import etree
from frappe import get_all, get_doc
from OpenSSL import crypto
import os
import logging

# Configurar el logger
logger = logging.getLogger(__name__)
handler = logging.FileHandler('/home/frappe/frappe-bench/apps/integracion/integracion/integracion/sii/logs/facturas_emitidas.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Ruta al archivo WSDL para facturas emitidas
wsdl_emitidas = '/home/frappe/frappe-bench/apps/integracion/integracion/integracion/sii/WSDL/SuministroFactEmitidas.wsdl'
client_emitidas = Client(wsdl=wsdl_emitidas)

# Definición de los certificados por empresa
certificados = {
    "Academia Técnica Universitaria SL": {
        "ruta": "/home/frappe/frappe-bench/apps/integracion/integracion/integracion/sii/certificate/ACADEMIA TECNICA.pfx",
        "password": "Grupo@tu#23"
    },
    # Añade aquí más empresas y sus certificados
}

def load_certificate(p12_file_path, p12_password):
    logger.info(f"Cargando el certificado desde {p12_file_path}")
    with open(p12_file_path, 'rb') as f:
        p12_data = f.read()
    p12 = crypto.load_pkcs12(p12_data, p12_password)
    logger.info("Certificado cargado con éxito")
    return p12

def sign_xml(xml_content, p12):
    logger.info("Firmando el XML")
    # Convert XML string to bytes
    xml_bytes = xml_content.encode('utf-8')
    
    # Load certificate and key
    cert = p12.get_certificate()
    key = p12.get_privatekey()
    
    # Create a PKCS7 object
    pkcs7 = crypto.PKCS7_sign(cert, key, xml_bytes, [], crypto.PKCS7_BINARY)
    
    # Convert PKCS7 to DER format
    der_bytes = crypto.dump_pkcs7(pkcs7)
    
    # Attach signature to the XML
    signed_xml = xml_content + '\n<!-- Signature -->\n' + der_bytes.hex()
    logger.info("XML firmado con éxito")
    return signed_xml

def obtener_factura_venta(docname):
    logger.info(f"Obteniendo la factura de venta: {docname}")
    return get_doc('Sales Invoice', docname)

def construir_xml_emitidas(facturas):
    logger.info("Construyendo el XML de las facturas emitidas")
    root = etree.Element("SuministroLRFacturasEmitidas", xmlns="https://www2.agenciatributaria.gob.es/static_files/common/internet/dep/aplicaciones/es/aeat/ssii/fact/ws/SuministroLR.xsd")
    for factura in facturas:
        registro = etree.SubElement(root, "RegistroLRFacturasEmitidas")
        id_factura = etree.SubElement(registro, "IDFactura")
        num_factura = etree.SubElement(id_factura, "NumSerieFacturaEmisor")
        num_factura.text = str(factura['name'])
        fecha = etree.SubElement(id_factura, "FechaExpedicionFacturaEmisor")
        fecha.text = str(factura['posting_date'])
        
        # Datos del cliente
        id_cliente = etree.SubElement(registro, "IDFactura")
        nombre_cliente = etree.SubElement(id_cliente, "NombreRazon")
        nombre_cliente.text = str(factura['customer_name'])
        nif_cliente = etree.SubElement(id_cliente, "NIF")
        nif_cliente.text = str(factura['tax_id'])
        
        # Totales
        total_factura = etree.SubElement(registro, "ImporteTotal")
        total_factura.text = str(factura['grand_total'])
        total_impuestos = etree.SubElement(registro, "TotalImpuestos")
        total_impuestos.text = str(factura['total_taxes_and_charges'])

    logger.info("XML construido con éxito")
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8')

def guardar_xml(xml_firmado, filename):
    logger.info(f"Guardando el XML firmado en {filename}")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_firmado)
    logger.info("XML guardado con éxito")

def enviar_facturas_emitidas(docnames):
    logger.info("Iniciando el proceso de envío de facturas emitidas")
    if isinstance(docnames, str):
        docnames = [docnames]
    
    facturas = [obtener_factura_venta(docname) for docname in docnames]
    xml_data = construir_xml_emitidas(facturas)
    
    # Obtener la empresa de la primera factura (asumiendo que todas las facturas son de la misma empresa)
    empresa = facturas[0].company
    logger.info(f"Empresa detectada: {empresa}")
    
    # Obtener el certificado correspondiente a la empresa
    certificado_info = certificados.get(empresa)
    if not certificado_info:
        logger.error(f"No se encontró un certificado para la empresa {empresa}")
        raise ValueError(f"No se encontró un certificado para la empresa {empresa}")
    
    p12_file_path = certificado_info['ruta']
    p12_password = certificado_info['password']
    
    # Cargar el certificado
    p12 = load_certificate(p12_file_path, p12_password)
    
    # Firmar el XML
    xml_firmado = sign_xml(xml_data.decode('utf-8'), p12)
    
    # Guardar el XML firmado
    current_directory = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(current_directory, f'facturas_emitidas_firmadas_{empresa}.xml')
    guardar_xml(xml_firmado, output_file)
    
    # Enviar el XML firmado (comentado)
    # logger.info("Enviando el XML firmado a la AEAT")
    # response = client_emitidas.service.SuministroLRFacturasEmitidas(xml_firmado)
    # logger.info(f"Respuesta de la AEAT: {response}")
    
    logger.info("Proceso de envío de facturas emitidas finalizado")
    return output_file
