from jinja2 import Environment, FileSystemLoader
from from_number_to_letters import Thousands_Separator, numero_a_letras
import pdfkit, os, env as _env
from django.conf import settings
from inventory.models import Product
from getpass import getuser
USER_WINDOWS = getuser()

def GeneratePDF(name_doc, path):
    path_dir = path
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)
    html_file_path = os.path.join(path_dir, f"{name_doc}.html")
    config = pdfkit.configuration(wkhtmltopdf=settings.URL_MAKE_PDF)
    pdf_file_path = os.path.join(path_dir, f"{name_doc}.pdf")
    pdfkit.from_file(html_file_path, pdf_file_path, configuration=config)

def Create_PDF_Invoice(data, file, file_name_save):
    path = data['path_dir']
    env = Environment(loader=FileSystemLoader("invoice/template_pdf/"))
    template = env.get_template(file+".html")
    name_doc = file_name_save
    subtotal = 0
    total = 0
    ipo = 0
    tax = {}
    tax_0 = 0
    tax_5 = 0
    tax_16 = 0
    discount = 0
    for i in data['details']:
        tax_product = int(i['tax_value'])
        if tax_product == 0:
            tax_0 += float(i['tax']) * float(i['quantity'])
        if tax_product == 5:
            tax_5 += float(i['tax']) * float(i['quantity'])
        if tax_product == 16:
            tax_16 += float(i['tax']) * float(i['quantity'])
        subtotal += i['cost'] * i['quantity']
        discount += i['discount'] * i['quantity']
        ipo += i['ipo'] * i['quantity']
        total += (i['cost'] * i['quantity']) + (i['tax'] * i['quantity']) + (i['ipo'] * i['quantity'])

        i['total_tax'] = i['tax'] * i['quantity']
        i['total_tax_money'] = Product.format_price(i['total_tax'])
        i['quantity'] = float(i['quantity'])
        i['price'] = float(i['cost'])
        i['price_money'] = Product.format_price(i['price'])
        i['tax'] = float(i['tax'])
        i['tax_money'] = Product.format_price(i['tax'])
        i['ipo'] = float(i['ipo'])
        i['ipo_money'] = Product.format_price(i['ipo'])
        i['subtotals'] = float(i['subtotals'])
        i['subtotals_money'] = Product.format_price(i['subtotals'])

    #if tax_16 > 0:
    data['tax_16'] = tax_16
    data['tax_16_money'] = Product.format_price(data['tax_16'])
    #if tax_5 > 5:
    data['tax_5'] = tax_5
    data['tax_5_money'] = Product.format_price(data['tax_5'])
    #if tax_0 > 0:
    data['tax_0'] = tax_0
    data['tax_0_money'] = Product.format_price(data['tax_0'])

    data['subtotals'] = float(subtotal)
    data['subtotals_money'] = Product.format_price(data['subtotals'])
    data['discount'] = float(discount)
    data['discount_money'] = Product.format_price(data['discount'])
    data['totals'] = float(total)
    data['totals_money'] = Product.format_price(data['totals'])
    data['ipo'] = float(ipo)
    data['ipo_money'] = Product.format_price(data['ipo'])
    data['total_letters'] = numero_a_letras(total).upper()
    data['type_invoice'] = int(data['type_document'])
    #print(data)
    html = template.render(data)
    html_file_path = os.path.join(path, f"{name_doc}.html")
    with open(html_file_path, 'w') as file:
        file.write(html)
    GeneratePDF(name_doc, path)
    os.remove(html_file_path)

def Create_PDF_Payment(data, file, file_name_save):
    path = data['path_dir']
    env = Environment(loader=FileSystemLoader("invoice/template_pdf/"))
    template = env.get_template(file+".html")
    name_doc = file_name_save
  
    #print(data)
    html = template.render(data)
    html_file_path = os.path.join(path, f"{name_doc}.html")
    with open(html_file_path, 'w') as file:
        file.write(html)
    GeneratePDF(name_doc, path)
    os.remove(html_file_path)
