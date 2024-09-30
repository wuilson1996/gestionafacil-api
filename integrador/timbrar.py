from zeep import Client
from lxml import etree
from zeep.plugins import HistoryPlugin

username = "ljimenez@finkok.com.mx"
password = "28Loo!04"

invoice_path = "/home/ljimenez/Documents/TimbradoScript/CartaPorte30.xml"
with open(invoice_path, "rb") as file:
    xml = file.read()

# Crear instancia de HistoryPlugin
history = HistoryPlugin()

xml_etree = etree.fromstring(xml)
comprobante = xml_etree
if comprobante is not None and 'Sello' in comprobante.attrib:
    has_stamp = True  # Indica que se encontró el sello
    print("Sello encontrado:")
else:
    has_stamp = False  # Indica que no se encontró el sello
    print("No se encontró el elemento Comprobante")

print("¿Tiene sello?", has_stamp)


if has_stamp:
    print("Timbrando con stamp")
    url = "https://demo-facturacion.finkok.com/servicios/soap/stamp.wsdl"
    contenido = Client(wsdl=url, plugins=[history]).service.stamp(xml, username, password)
else:
    print("Timbrando con sign_stamp")
    url = "https://demo-facturacion.finkok.com/servicios/soap/stamp.wsdl"
    contenido = Client(wsdl=url, plugins=[history]).service.sign_stamp(xml, username, password)

# Obtener la solicitud SOAP como cadena de texto XML
request_xml = etree.tostring(history.last_sent["envelope"], encoding="unicode")

# Guardar la solicitud SOAP en un archivo
with open("request.xml", "w", encoding="utf-8") as req_file:
    req_file.write(request_xml)

# Obtener la respuesta SOAP como cadena de texto XML
response_xml = etree.tostring(history.last_received["envelope"], encoding="unicode")

# Guardar la respuesta SOAP en un archivo
with open("response.xml", "w", encoding="utf-8") as res_file:
    res_file.write(response_xml)

# Obtener XML timbrado
xml_timbrado = contenido.xml
print(contenido)

# Guardar XML timbrado en un archivo en formato bytes
with open("stamp.xml", "wb") as archivo:
    archivo.write(xml_timbrado.encode("utf-8"))
