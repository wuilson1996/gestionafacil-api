from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import xml.etree.ElementTree as ET

# Leer el XML de la factura electrónica
tree = ET.parse('C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/documents/invoice1.xml')
root = tree.getroot()

# Crear un lienzo PDF
pdf_filename = 'C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/documents/factura.pdf'
c = canvas.Canvas(pdf_filename, pagesize=letter)

# Definir la función para agregar texto al PDF
def add_text(x, y, text):
    c.drawString(x, y, text)

# Definir la función para agregar una tabla al PDF
def add_table(x, y, data):
    table_height = len(data) * 20
    table_width = 400
    row_height = 20
    col_width = table_width / len(data[0])

    for i, row in enumerate(data):
        for j, cell in enumerate(row):
            c.rect(x + j * col_width, y - i * row_height, col_width, row_height)
            add_text(x + j * col_width + 5, y - i * row_height - 10, cell)

# Agregar los datos del emisor
emisor = root.find('.//{http://www.sat.gob.mx/cfd/4}Emisor')
rfc_emisor = emisor.get('Rfc', '')
nombre_emisor = emisor.get('Nombre', '')

# Agregar los datos del receptor
receptor = root.find('.//{http://www.sat.gob.mx/cfd/4}Receptor')
rfc_receptor = receptor.get('Rfc', '')
nombre_receptor = receptor.get('Nombre', '')

# Agregar los datos generales de la factura
folio = root.get('Folio', '')
fecha = root.get('Fecha', '')
subtotal = root.get('SubTotal', '')
total = root.get('Total', '')
moneda = root.get('Moneda', '')
tipo_comprobante = root.get('TipoDeComprobante', '')
forma_pago = root.get('FormaPago', '')
metodo_pago = root.get('MetodoPago', '')
lugar_expedicion = root.get('LugarExpedicion', '')

# Agregar los datos del emisor y receptor al PDF
add_text(100, 750, 'Emisor:')
add_text(120, 730, f'RFC: {rfc_emisor}')
add_text(120, 710, f'Nombre: {nombre_emisor}')

add_text(350, 750, 'Receptor:')
add_text(370, 730, f'RFC: {rfc_receptor}')
add_text(370, 710, f'Nombre: {nombre_receptor}')

# Agregar los datos generales de la factura al PDF
add_text(100, 670, f'Folio: {folio}')
add_text(100, 650, f'Fecha: {fecha}')
add_text(100, 630, f'Subtotal: {subtotal}')
add_text(100, 610, f'Total: {total}')
add_text(100, 590, f'Moneda: {moneda}')
add_text(100, 570, f'Tipo de Comprobante: {tipo_comprobante}')
add_text(100, 550, f'Forma de Pago: {forma_pago}')
add_text(100, 530, f'Método de Pago: {metodo_pago}')
add_text(100, 510, f'Lugar de Expedición: {lugar_expedicion}')

# Agregar los datos de los conceptos de la factura
conceptos = []
for concepto in root.findall('.//{http://www.sat.gob.mx/cfd/4}Concepto'):
    descripcion = concepto.get('Descripcion', '')
    cantidad = concepto.get('Cantidad', '')
    importe = concepto.get('Importe', '')
    conceptos.append([descripcion, cantidad, importe])
add_table(100, 470, [['Descripción', 'Cantidad', 'Importe']] + conceptos)

# Agregar los impuestos trasladados
traslados = root.find('.//{http://www.sat.gob.mx/cfd/4}Impuestos/{http://www.sat.gob.mx/cfd/4}Traslados')
if traslados is not None:
    impuestos_trasladados = []
    for traslado in traslados.findall('.//{http://www.sat.gob.mx/cfd/4}Traslado'):
        impuesto = traslado.get('Impuesto', '')
        importe = traslado.get('Importe', '')
        impuestos_trasladados.append([impuesto, importe])
    add_table(100, 270, [['Impuesto Trasladado', 'Importe']] + impuestos_trasladados)

# Agregar los impuestos retenidos
retenciones = root.find('.//{http://www.sat.gob.mx/cfd/4}Impuestos/{http://www.sat.gob.mx/cfd/4}Retenciones')
if retenciones is not None:
    impuestos_retenidos = []
    for retencion in retenciones.findall('.//{http://www.sat.gob.mx/cfd/4}Retencion'):
        impuesto = retencion.get('Impuesto', '')
        importe = retencion.get('Importe', '')
        impuestos_retenidos.append([impuesto, importe])
    add_table(100, 70, [['Impuesto Retenido', 'Importe']] + impuestos_retenidos)

# Guardar el PDF
c.save()