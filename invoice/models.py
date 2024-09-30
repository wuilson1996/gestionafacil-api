from django.db import models
from user.models import Employee
from company.models import Branch, License, Resolution, Bank, SerieFolio
from inventory.models import Product, Supplier, Store
from customer.models import *
from django.core import serializers
from setting.models import *
from datetime import date, datetime, timedelta
import json, qrcode, env
from io import BytesIO
from django.core.files import File
from PIL import Image
from .make_pdf import *
from django.conf import settings
from .Email import *

class Invoice(models.Model):
	INVOICE = 1
	INVOICE_TRANSFER = 2
	TICKET = 3
	NC = 4
	TICKET_INVOICE = 5

	TYPE_DOCUMENT = (
		(INVOICE, "Invoice"), # ingresos e ingresos de traslado. I
		(INVOICE_TRANSFER, "Invoice Transfer"),# ingresos e ingresos de traslado. I
		(TICKET, "Ticket"),
		(NC, "Nota Credito"),
		(TICKET_INVOICE, "Ticket invoice"),
	)
	type_document = models.IntegerField(choices=TYPE_DOCUMENT, default=INVOICE)
	number = models.IntegerField()
	prefix = models.CharField(max_length = 7)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	date = models.CharField(max_length = 12)
	time = models.TimeField(auto_now_add = True)
	total = models.FloatField(null = True, blank = True)
	paid = models.FloatField(null = True, blank = True)
	note = models.TextField(null = True, blank = True)
	pie_invoice = models.TextField(null = True, blank = True)
	term_and_cond = models.TextField(null = True, blank = True)
	seller_info = models.ForeignKey(SellerInfo, on_delete = models.CASCADE, null=True, blank=True)
	customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
	cancelled = models.BooleanField(default = True)
	hidden = models.BooleanField(default = False)
	STATE = (
		("Timbrada", "Timbrada"),
		("No timbrada", "No timbrada"),
		("Cancelado", "Cancelado"),
		("Vigente", "Vigente"),
	)
	state = models.CharField(choices=STATE, max_length = 256, null = True, blank = True, default="No timbrada")
	STATE_INVOICE = (
		("Pagada", "Pagada"),
		("Borrador", "Borrador"),
		("Cancelado", "Cancelado"),
		("Vigente", "Vigente"),
		("Por cobrar", "Por cobrar"),
	)
	state_invoice = models.CharField(choices=STATE_INVOICE, max_length = 256, null = True, blank = True)
	STATE_EMAIL = (
		("Email enviado", "Email enviado"),
		("Email no enviado", "Email no enviado"),
	)
	state_email = models.CharField(choices=STATE_EMAIL, max_length = 256, null=True, blank=True, default="Email no enviado")
	
	no_cert_dig = models.CharField(max_length = 100, null=True, blank=True)
	cadena_original = models.CharField(max_length = 3024,null = True, blank = True)
	
	sello_cfdi = models.CharField(max_length = 2024,null = True, blank = True)
	no_cert_sat = models.CharField(max_length = 100, null=True, blank=True)
	UUID = models.CharField(max_length = 1024,null = True, blank = True)
	cufe = models.CharField(max_length = 1024,null = True, blank = True) # SatSeal Sello de SAT
	date_cert = models.CharField(max_length = 12, null=True, blank=True)

	pdf = models.CharField(max_length=1024, null=True, blank=True)
	
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE, null = True, blank = True)
	uso_cfdi = models.ForeignKey(CFDI, on_delete = models.CASCADE, null = True, blank = True)
	reason_cancel = models.ForeignKey(MotivoCancel, on_delete = models.CASCADE, null = True, blank = True)

	status_file = models.TextField(null = True, blank = True)

	timbre_path = "media/timbres/"
	annulled = models.BooleanField(default = False)

	def __str__(self):
		return f"{self.prefix} - {self.number} by {self.branch.name} - Type Document: {self.type_document}"

	@classmethod
	def send_email(cls, data):
		try:
			_invoice = Invoice.objects.filter(pk = data["pk_invoice"]).first()
			if _invoice.status_file == "Success":
				_pdf = _invoice.branch.company.documentI+str(_invoice.prefix)+str(_invoice.number)+".pdf"
				_xml = _invoice.branch.company.documentI+str(_invoice.prefix)+str(_invoice.number)+".xml"
				email_smtp = EmailSMTP.objects.all().last()
				email_send = MessageEmail.objects.filter(type_message=MessageEmail.SEND_FILE).first()
				send(
                    email_smtp.email,
                    email_smtp.password,
                    data["email"],
                    email_send.asunto,
                    email_send.message,
                    "",
                    cls.timbre_path,
                    _pdf,
                    _xml,
                    email_smtp.host,
                    email_smtp.port
                )
				result = {
                    "status": "OK",
                    "code": 200,
                    "message": "Email enviando correctamente."
                }
				_invoice.state_email = "Email enviado"
				_invoice.save()
			else:
				result = {
                    "status": "Fail",
                    "code": 400,
                    "message": "Fallo al enviar documento."
                }
		except Exception as e:
			result = {
                "status": "Fail",
                "code": 400,
                "message": str(e)
            }
			_invoice.state_email = str(e)
			_invoice.save()
		return result

	@staticmethod
	def generate_qr_code(data,name_qr):
		result = False
		message = None
		try:
			qr = qrcode.QRCode(
			    version=1,
			    error_correction=qrcode.constants.ERROR_CORRECT_L,
			    box_size=10,
			    border=4,
			)
			qr.add_data(data)
			qr.make(fit=True)
			img = qr.make_image(fill_color="rgb(0, 0, 255)", back_color="rgb(255, 255, 255)")
			img = img.convert("RGBA")
			buffer = BytesIO()
			img.save(f"{env.URL_QR_IN_USE}{name_qr}.png")
		except Exception as e:
			message = str(e)
		return buffer

	@classmethod
	def generate_qr_code_view(cls, data):
		invoice = Invoice.get_invoice(data['pk_invoice'])
		name_qr = f"{invoice['prefix']}{invoice['number']}"
		time = datetime.strptime(invoice['time'], "%H:%M:%S.%f")
		invoice_data = f"""Factura: {invoice['prefix']}{invoice['number']}\nEstablecimiento: {invoice['branch']['name']}\nFecha: {invoice['date']}\nHora: {time.strftime("%H:%M:%S")}\nTotal de la factura{invoice['total']}\nNombre del Cliente: {invoice['customer']['name']}"""
		qr_code_buffer = cls.generate_qr_code(invoice_data, name_qr)
		return True

	@classmethod
	def send_invoice_dian(cls, data):
		result = False
		message = None
		_data = None
		try:
			invoice = Invoice.get_invoice(data['pk_invoice'])
			if invoice is not None:
				_data = Send_Dian(invoice).Send(data['type_document'])
				message = "Success"
				result = True
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message, 'data': _data}

	@classmethod
	def get_selling_by_invoice(cls, data):
		return {'total':sum( int(json.loads(serializers.serialize('json', [i]))[0]['fields']['total']) for i in cls.objects.filter(type_document=data['type_document'], branch= Branch.objects.get(pk = data['pk_branch']), date = date.today()) )}

	@classmethod
	def get_selling_by_date(cls, data):
		branch = Branch.objects.get(pk=data['pk_branch'])
		start_date = datetime.strptime(data['date_start'], '%Y-%m-%d').date()
		end_date = date.today() + timedelta(days=1)
		totals_by_date = {str(start_date + timedelta(days=i)): 0 for i in range((end_date - start_date).days)}
		invoice = cls.objects.filter(branch=branch, date__range=(start_date, end_date))
		for i in invoice:
			invoice_date = str(i.date)
			total = int(i.total)
			totals_by_date[invoice_date] = totals_by_date.get(invoice_date, 0) + total
		return totals_by_date

	@classmethod
	def get_invoice(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				_invoice = cls.objects.get(pk = data['pk_invoice'])
				#print(_invoice)
				serialized_invoice = serializers.serialize('json', [_invoice])
				invoice = json.loads(serialized_invoice)[0]
				result["data"] = invoice['fields']
				result["data"]['pk_invoice'] = data['pk_invoice']
				list_details = []
				if _invoice.type_document != 5:
					for i in Details_Invoice.objects.filter(invoice = _invoice):
						serialized_product = serializers.serialize('json', [i])
						product = json.loads(serialized_product)[0]['fields']
						product['subtotals'] = (product['price'] + product['ipo']) * product['quantity']
						product["pk_item"] = i.pk
						product["pk"] = i.product.pk
						product["description"] = i.product.description
						product["clave_uni_name"] = i.product.unit_measure.name
						product["clave_uni"] = i.product.unit_measure.clave
						product["clave_uni_type"] = i.product.unit_measure.tipo
						product["price_money"] = Product.format_price(product['subtotals'])
						list_details.append(product)

					try:
						result["data"]['payment_form_data'] = json.loads(serializers.serialize('json', [Payment_Forms.objects.get(invoice = _invoice).payment_form]))[0]['fields']
						result["data"]['payment_method_data'] = json.loads(serializers.serialize('json', [Payment_Forms.objects.get(invoice = _invoice).payment_method]))[0]['fields']
					except Exception as e01:
						print(e01)
					
					if _invoice.type_document == 4:
						result["data"]["invoice_rt"] = []
						for irt in CreditNote.objects.filter(nc_to_invoice = NcToInvoice.objects.filter(invoice = _invoice).first()):
							result["data"]["invoice_rt"].append(irt.invoice.pk)
					
					result["data"]['payments'] = []
					try:
						if _invoice.type_document == 1:
							payment_to_pay = PaymentToPayInvoice.objects.filter(invoice=_invoice).first()
							_total_p = 0
							for _payment in PaymentInvoice.objects.filter(invoice = _invoice):
								_total_p += _payment.amount
								result["data"]['payments'].append({
									"pk": _payment.pk,
									"number": _payment.number,
									"total": Product.format_price(_payment.invoice.total),
									'paid': Product.format_price(_payment.amount),
									'to_pay': Product.format_price(payment_to_pay.amount - _total_p),
								})
							m = MessageToInvoice.objects.filter(invoice=_invoice).first()
							result["data"]["comment"] = m.text if m else ""
					except Exception as e:
						print("Error: "+str(e))
				else:
					ift = InvoiceFromTicket.objects.filter(invoice=_invoice).first()
					for detail in TicketGeneral.objects.filter(invoice_from_ticket = ift):
						serialized_ticket = serializers.serialize('json', [detail.invoice])
						_ticket = json.loads(serialized_ticket)[0]['fields']
						_ticket["pk_invoice"] = detail.invoice.pk
						try:
							payment_form_data = json.loads(serializers.serialize('json', [Payment_Forms.objects.get(invoice = detail.invoice).payment_form]))[0]['fields']
							payment_method_data = json.loads(serializers.serialize('json', [Payment_Forms.objects.get(invoice = detail.invoice).payment_method]))[0]['fields']
						except Exception as e:
							print("Error payment types: "+str(e))
							payment_form_data = {}
							payment_method_data = {}
						_ticket["payment_form"] = payment_form_data
						_ticket["payment_method"] = payment_method_data

						_ticket["notas"] = detail.invoice.note
						
						_ticket["clave_uni_name"] = "Actividad"
						_ticket["clave_uni"] = "ACT"
						_ticket["clave_uni_type"] = "Unidades de venta"
						_ticket["code"] = "01010101"
						_ticket["name"] = "Venta"
						_ticket["price_money"] = Product.format_price(detail.invoice.total)

						_ticket["details"] = []
						__tax_value = 0
						__tax = 0
						for j in Details_Invoice.objects.filter(invoice = detail.invoice):
							serialized_product = serializers.serialize('json', [j])
							product = json.loads(serialized_product)[0]['fields']
							product['subtotals'] = (product['price'] + product['ipo']) * product['quantity']
							product["pk_item"] = j.pk
							product["pk"] = j.product.pk
							product["description"] = j.product.description
							product["clave_uni_name"] = j.product.unit_measure.name
							product["clave_uni"] = j.product.unit_measure.clave
							product["clave_uni_type"] = j.product.unit_measure.tipo
							product["price_money"] = Product.format_price(product['subtotals'])
							_ticket["details"].append(product)
							__tax_value = j.tax_value
							__tax += j.tax
						
						_ticket["tax_value"] = __tax_value
						_ticket["tax"] = __tax
						_ticket["quantity"] = 1
						_ticket["cost"] = detail.invoice.total - __tax
						_ticket["discount"] = 0
						_ticket["ipo"] = 0
						_ticket["subtotals"] = detail.invoice.total
						_ticket["total"] = detail.invoice.total - __tax
						list_details.append(_ticket)
					result["data"]["invoice_from_ticket"] = json.loads(serializers.serialize('json', [ift]))[0]['fields']
					result["data"]["invoice_from_ticket"]["pk"] = ift.pk

					try:
						result["data"]['payment_form_data'] = json.loads(serializers.serialize('json', [Payment_Form.objects.filter(pk = 3).first()]))[0]['fields']
						result["data"]['payment_method_data'] = json.loads(serializers.serialize('json', [Payment_Method.objects.filter(code = "PUE").first()]))[0]['fields']
					except Exception as e02:
						print(e02)
				result["data"]["total"] = Product.format_price(_invoice.total)
				result["data"]['details'] = list_details
				serialized_paymentform = serializers.serialize('json', [Payment_Forms.objects.get(invoice = _invoice)])
				result["data"]['payment_form'] = json.loads(serialized_paymentform)[0]['fields']

				result["data"]['company'] = json.loads(serializers.serialize('json', [_invoice.branch.company]))[0]['fields']
				try:
					result["data"]['company']["postal_code"] = str(_invoice.branch.company.address).split(",")[0]
				except Exception as epc:
					print("Error Postal Code: "+str(epc))
				result["data"]['metod'] = "Crédito" if result["data"]['payment_form'] == 2 else "Efectivo"
				_customer = Customer.objects.get(pk = _invoice.customer.pk)
				serialized_customer = serializers.serialize('json', [_customer])
				result["data"]['customer'] = json.loads(serialized_customer)[0]['fields']
				_branch = Branch.objects.get(pk = _invoice.branch.pk)
				branch = serializers.serialize('json', [_branch])
				result["data"]['branch'] = json.loads(branch)[0]['fields']
				result["data"]["SatSeal"] = result["data"]["cufe"]
				try:
					result["data"]["company"]["regimen_data"] = json.loads(serializers.serialize('json', [Type_Regimen.objects.filter(pk = result["data"]['company']["type_regime"]).first()]))[0]['fields']
				except Exception as e:
					print("Error regimen company: "+str(e))
				try:
					result["data"]["customer"]["regimen_data"] = json.loads(serializers.serialize('json', [Type_Regimen.objects.filter(pk = result["data"]['customer']["type_regime"]).first()]))[0]['fields']
				except Exception as e:
					print("Error regimen client: "+str(e))
				try:
					result["data"]["customer"]["uso_cfdi"] = json.loads(serializers.serialize('json', [Commercial_Information.objects.filter(customer = _customer).first().cfdi]))[0]['fields']
					result["data"]["customer"]["payment_method"] = json.loads(serializers.serialize('json', [Commercial_Information.objects.filter(customer = _customer).first().payment_method]))[0]['fields']
					result["data"]["customer"]["payment_form"] = json.loads(serializers.serialize('json', [Commercial_Information.objects.filter(customer = _customer).first().payment_form]))[0]['fields']
				except Exception as e:
					print("Error cfdi client: "+str(e))
				try:
					result["data"]["uso_cfdi"] = json.loads(serializers.serialize('json', [_invoice.uso_cfdi]))[0]['fields']
					result["data"]["uso_cfdi"]["pk"] = _invoice.uso_cfdi.pk
					print(result["data"]["uso_cfdi"])
				except Exception as e:
					print("Error cfdi invoice: "+str(e))
					if _invoice.type_document == 5:
						_cfdi = CFDI.objects.filter(code="S01").first()
						result["data"]["uso_cfdi"] = json.loads(serializers.serialize('json', [_cfdi]))[0]['fields']
						result["data"]["uso_cfdi"]["pk"] = _cfdi.pk
				try:
					_payment_to_pay = PaymentToPayInvoice.objects.filter(invoice=_invoice).first()
					result["data"]['payment_to_pay'] = json.loads(serializers.serialize('json', [_payment_to_pay]))[0]['fields']
					result["data"]['payment_to_pay']["credit"] = Product.format_price(_invoice.total - _payment_to_pay.amount)
					result['data']["payment_to_pay"]['date'] = str(_payment_to_pay.date.date())
				except Exception as e:
					print("Error payments invoice: "+str(e))

				resolution = {}
				try:
					resolution = serializers.serialize('json', [Resolution.objects.get(branch= _branch, type_document_id = result["data"]['type_document'])])
					result["data"]['resolution'] = json.loads(resolution)[0]['fields']
				except Exception as err:
					result["data"]['resolution'] = {}
				
				_emails = [_invoice.customer.email]
				for p in Associate_Person.objects.filter(customer = _invoice.customer):
					_emails.append(p.email)
				
				result["data"]["emails"] = _emails
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"
		except Exception as err2:
			result['message'] = str(err2)
			print("Error general: "+str(err2))
		return result

	@classmethod
	def annulled_invoice(cls, data):
		result = False
		message = None
		try:
			invoice = cls.objects.get(pk = data['pk_invoice'], annulled = False)
			invoice.total = 0
			invoice.annulled = True
			invoice.state = "Factura Anulada."
			invoice.save()
			for i in Details_Invoice.objects.filter(invoice = invoice):
				product = Product.objects.get(code = i.code)
				product.quantity += i.quantity
				product.save()
			result = True
			message = "Success"
			employee = Employee.objects.get(pk = data['pk_employee'])
			serialized_employee = serializers.serialize('json', [employee])
			employee = json.loads(serialized_employee)[0]['fields']
			serialized_invoice = serializers.serialize('json', [invoice])
			invoice = json.loads(serialized_invoice)[0]['fields']
			History_Invoice.create_history_invoice(invoice, employee, 'Annulled')
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

	@classmethod
	def annulled_invoice_by_product(cls, data):
		result = False
		message = None
		try:
			invoice = cls.objects.get(pk=data['pk_invoice'], annulled=False)
			for detail_invoice in Details_Invoice.objects.filter(invoice=invoice):
				product = Product.objects.get(code=data['code'])
				quantity = int(data['quantity'])
				if detail_invoice.quantity > 0:
					product.quantity += quantity
					total = round((detail_invoice.cost + detail_invoice.tax) * (detail_invoice.quantity - quantity))
					detail_invoice.price = total
					detail_invoice.quantity -= quantity
					invoice.note = ''
					product.save()
					detail_invoice.save()
					invoice.total = total
					invoice.save()
					data_invoice = Invoice.get_invoice(data['pk_invoice'])
					Credi_Note_Product(
	                	data_invoice,
	                	data['code'], data['quantity'], 1, "Devolucion de producto",
	                	Resolution.get_number(9)
	                ).Send()
					total_ncp = round((detail_invoice.cost + detail_invoice.tax) * quantity)
					quantity_send = Note_Credit_Product.create_nc_by_product(detail_invoice, quantity, total_ncp, invoice)
					invoice.note += f"Se aplico nota credito al producto {product.name} - Codigo {product.code} | Quitando {quantity_send['quantity_send']} productos\n"
					invoice.save()
					result = True
					message = "Success"
				else:
					message = "The product is already at zero"
		except cls.DoesNotExist:
			message = "Invoice does not exist"
		except Details_Invoice.DoesNotExist:
			message = "Invoice details do not exist"
		except Product.DoesNotExist:
			message = "Product does not exist"
		except Exception as e:
			message = str(e)
		return {'result': result, 'message': message}

	@classmethod
	def get_list_invoice(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"data": []
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				#print(data['type_document'])
				for i in cls.objects.filter(branch = branch, type_document = data['type_document']).order_by('-pk'):
					#print(i)
					_payment_to_pay = PaymentToPayInvoice.objects.filter(invoice=i).first()
					
					list_details = []
					if data['type_document'] != 5:
						for detail in Details_Invoice.objects.filter(invoice = i):
							serialized_product = serializers.serialize('json', [detail])
							product = json.loads(serialized_product)[0]['fields']
							product['subtotals'] = (product['price'] + product['ipo']) * product['quantity']
							product["pk_item"] = detail.pk
							product["pk"] = detail.product.pk
							product["description"] = detail.product.description
							product["price_money"] = Product.format_price(detail.product.price_1)
							list_details.append(product)
					else:
						ift = InvoiceFromTicket.objects.filter(invoice=i).first()
						for detail in TicketGeneral.objects.filter(invoice_from_ticket = ift):
							serialized_ticket = serializers.serialize('json', [detail.invoice])
							_ticket = json.loads(serialized_ticket)[0]['fields']
							_ticket["pk"] = detail.invoice.pk
							try:
								payment_form_data = json.loads(serializers.serialize('json', [Payment_Forms.objects.get(invoice = detail.invoice).payment_form]))[0]['fields']
								payment_method_data = json.loads(serializers.serialize('json', [Payment_Forms.objects.get(invoice = detail.invoice).payment_method]))[0]['fields']
							except Exception as e:
								print("Error payment types: "+str(e))
								payment_form_data = {}
								payment_method_data = {}
							_ticket["payment_form"] = payment_form_data
							_ticket["payment_method"] = payment_method_data
							_ticket["notas"] = detail.invoice.note
							_ticket["total"] = Product.format_price(detail.invoice.total)
							list_details.append(_ticket)
					
					_emails = [i.customer.email]
					for p in Associate_Person.objects.filter(customer = i.customer):
						_emails.append(p.email)

					try:
						payment_form_data = json.loads(serializers.serialize('json', [Payment_Forms.objects.get(invoice = i).payment_form]))[0]['fields']
						payment_method_data = json.loads(serializers.serialize('json', [Payment_Forms.objects.get(invoice = i).payment_method]))[0]['fields']
					except Exception as e:
						print("Error payment types: "+str(e))
						payment_form_data = {}
						payment_method_data = {}

					result["data"].append(
						{
							"type_document":i.type_document,
							'pk_invoice': i.pk,
							'number': i.number,
							'prefix': i.prefix,
							'date': i.date,
							'expiration': _payment_to_pay.date.date() if _payment_to_pay else None,
							'name_client': i.customer.name,
							'pk_customer': i.customer.pk,
							'documentI': i.customer.identification_number,
							'total': Product.format_price(i.total if i.total else 0),
							'paid': Product.format_price(_payment_to_pay.amount) if _payment_to_pay else None,
							'to_pay': Product.format_price(i.total - _payment_to_pay.amount) if _payment_to_pay else None,
							"state":i.state,
							"state_invoice": i.state_invoice,
							"cancelled":i.cancelled,
							"annulled":i.annulled,
							"pdf": i.pdf,
							"date_cert": i.date_cert,
							"notas": i.note,
							"details": list_details,
							"emails": _emails,
							"payment_form": payment_form_data,
							"payment_method": payment_method_data
						}
					)
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"

		except Exception as e:
			result['message'] = str(e)
			print(e)
		return result

	@classmethod
	def create_invoice(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"pk_invoice": None
		}
		total = 0
		#try:			
		if Employee.check_by_token(token=data["token"]):
				customer = Customer.objects.get(pk = data['pk_customer'])
				employee = Employee.search_by_token(data['token'])
				branch = employee.branch
				validate = License.validate_date(branch)
				if validate['result']:
					license = License.discount_license(branch)
					if license['result']:
						# validate invoice create or modified
						invoice = cls.objects.filter(pk=data["pk"]).first()
						if not invoice:
							# create invoice
							invoice = cls(
								type_document = data['type_document'],
								number = data['number'],
								prefix = data['prefix'],
								branch = branch,
								date = data['date'],
								note = data['note'],
								customer = customer,
								seller_info = Commercial_Information.objects.filter(customer=customer).first().seller_info if Commercial_Information.objects.filter(customer=customer).first() else None,
								hidden = True if data['type_document'] == 99 else False,
								state_invoice = data['state'],
								employee = employee,
								uso_cfdi = CFDI.objects.filter(pk = data["uso"]).first(),
								pie_invoice = data["pieInvoice"],
								term_and_cond = data["termAndCond"]
							)
							invoice.save()
							result["pk_invoice"] = invoice.pk
							if data["type_document"] != 5:
								state = True
								if data["type_document"] == 3:
									_ticket_general = TicketGeneral.objects.create(invoice=invoice)
								elif data["type_document"] == 4:
									# process nc
									nc_to_invoice = NcToInvoice.objects.create(invoice=invoice)
									from company.models import Consecutive
									Consecutive.consecutive_increment("nc", branch)
									for irt in data["invoice_rt"]:
										CreditNote.objects.create(
											nc_to_invoice = nc_to_invoice,
											invoice = Invoice.objects.filter(pk = int(irt)).first()
										)
								elif invoice.type_document == 1:
									MessageToInvoice.objects.create(invoice=invoice, text=data["comment"])

							else:
								state = False
							if state:
								for i in data['details']:
									value = Details_Invoice.create_details(i, invoice)
									if not value['result']:
										state = False
										result['message'] = value['message']
										break
									else:
										state = value['result']
										result['message'] = value['message']
										total += float(value['total'])
							else:
								# asociate ticket with invoice
								ift = InvoiceFromTicket.objects.create(invoice=invoice, period=data["period"], month=data["month"])
								for tkt in data["details"]:
									ticket_invoice = TicketGeneral.objects.filter(invoice=Invoice.objects.filter(pk = int(tkt)).first()).last()
									ticket_invoice.invoice_from_ticket = ift
									ticket_invoice.save()
									total += ticket_invoice.invoice.total
								state = True

							if state:
								value = Payment_Forms.create_paymentform(data, invoice, employee)
								state = value['result']
								result['message'] = value['message']
								if state:
								
									invoice.total = total
									#invoice.paid = total
									invoice.save()
									values_wallet = {"pk_customer":customer.pk, 'amount_invoice':total}
									#Wallet_Customer.update_coins(values_wallet)
									_data = {'type_document':data['type_document'], 'pk_branch':branch.pk}
									#Resolution.add_number(_data)
									#serialized_employee = serializers.serialize('json', [employee])
									#employee = json.loads(serialized_employee)[0]['fields']
									serialized_invoice = serializers.serialize('json', [invoice])
									invoice = json.loads(serialized_invoice)[0]
									#History_Invoice.create_history_invoice(invoice, employee, 'Created',branch)
									HistoryGeneral.create_history(
										action=HistoryGeneral.CREATED,
										class_models=HistoryGeneral.INVOICE,
										class_models_json=invoice,
										employee=employee.pk,
										username=employee.user_django.username,
										branch=employee.branch.pk
									)
								else:
									invoice.delete()
							
							from company.models import SerieFolio
							SerieFolio.increment_serie_folio({"token": data["token"], "type_document": "Factura de venta", "pk": data["pk_serie_folio"]})
							result['message'] = "Factura guardada correctamente."
							
						else:
							# update invoice
							#print(data)
							invoice.type_document = data['type_document']
							#invoice.number = data['number']
							#invoice.prefix = data['prefix']
							invoice.branch = branch
							invoice.date = data['date']
							invoice.note = data['note']
							invoice.customer = customer
							invoice.seller_info = Commercial_Information.objects.filter(customer=customer).first().seller_info if Commercial_Information.objects.filter(customer=customer).first() else None
							invoice.hidden = True if data['type_document'] == 99 else False
							invoice.state_invoice = data['state']
							invoice.employee = employee
							invoice.uso_cfdi = CFDI.objects.filter(pk = data["uso"]).first()
							invoice.pie_invoice = data["pieInvoice"]
							invoice.term_and_cond = data["termAndCond"]
							invoice.save()

							# crear productos.
							result["pk_invoice"] = invoice.pk
							if data["type_document"] != 5:
								state = True
								if data["type_document"] == 3:
									_ticket_general = TicketGeneral.objects.filter(invoice=invoice).first()
									if not _ticket_general:
										_ticket_general = TicketGeneral.objects.create(invoice=invoice)
								elif data["type_document"] == 4:
									nc_to_invoice = NcToInvoice.objects.filter(invoice=invoice).first()
									if not nc_to_invoice:
										nc_to_invoice = NcToInvoice.objects.create(invoice=invoice)

									for irt in CreditNote.objects.filter(nc_to_invoice = nc_to_invoice):
										irt.delete()

									for irt in data["invoice_rt"]:
										CreditNote.objects.create(
											nc_to_invoice = nc_to_invoice,
											invoice = Invoice.objects.filter(pk = int(irt)).first()
										)

							else:
								state = False
							if state:
								# buscamos los productos asociados y comparamos con los productos que vienen en la solicitud.
								# eliminar productos que ya no estan en uso y actualizar productos.
								for p in Details_Invoice.objects.filter(invoice=invoice):
									state = False
									for p2 in data["details"]:
										if p2["pk_item"] != 0:
											if p2["pk_item"] == p.pk:
												# actualizar producto.
												p.quantity = p2["quantity"]
												p.cost = p2["cost"]
												p.price = p2["price"]
												p.tax = p2["tax"]
												p.save()

												state = True
												total += float(p2['totalValue'])
												break
									if not state:
										p.delete()
								for i in data['details']:
									if i["pk_item"] == 0:
										value = Details_Invoice.create_details(i, invoice)
										if not value['result']:
											state = False
											result['message'] = value['message']
											break
										else:
											state = value['result']
											result['message'] = value['message']
											total += float(value['total'])
							else:
								# asociate ticket with invoice
								ift = InvoiceFromTicket.objects.filter(invoice=invoice).first()
								if not ift:
									ift = InvoiceFromTicket.objects.create(invoice=invoice)
								
								ift.period=data["period"]
								ift.month=data["month"]
								ift.save()
								
								for tkt in TicketGeneral.objects.filter(invoice_from_ticket=ift):
									tkt.invoice_from_ticket = None
									tkt.save()

								for tkt in data["details"]:
									ticket_invoice = TicketGeneral.objects.filter(invoice=Invoice.objects.filter(pk = int(tkt)).first()).last()
									ticket_invoice.invoice_from_ticket = ift
									ticket_invoice.save()
									total += ticket_invoice.invoice.total
								state = True

							if state:
	
								value = Payment_Forms.create_paymentform(data, invoice, employee)
								state = value['result']
								result['message'] = value['message']
								if state:
									invoice.total = total#float(data["totalValue"])
									#invoice.paid = float(data["totalValue"])
									invoice.save()
									values_wallet = {"pk_customer":customer.pk, 'amount_invoice':total}
									#Wallet_Customer.update_coins(values_wallet)
									_data = {'type_document':data['type_document'], 'pk_branch':branch.pk}
									#Resolution.add_number(_data)
									#serialized_employee = serializers.serialize('json', [employee])
									#employee = json.loads(serialized_employee)[0]['fields']
									serialized_invoice = serializers.serialize('json', [invoice])
									invoice = json.loads(serialized_invoice)[0]
									#History_Invoice.create_history_invoice(invoice, employee, 'Updated',branch)
									HistoryGeneral.create_history(
										action=HistoryGeneral.UPDATE,
										class_models=HistoryGeneral.INVOICE,
										class_models_json=invoice,
										employee=employee.pk,
										username=employee.user_django.username,
										branch=employee.branch.pk
									)
							
							result['message'] = "Factura actualizada correctamente."
						result['code'] = 200
						result['status'] = "OK"
					else:
						result["message"] = license['message']
				else:
					result["message"] = validate['message']
		#except Exception as e:
		#	result["message"] = str(e)
		#	print(e, 'Created Invoice')
		return result

	@classmethod
	def get_list_invoice_credit(cls, branch):
		return [
			{
				"pk_invoice" : i.pk,
				"number": i.number,
				"prefix": i.prefix,
				"date": i.date,
				"total": i.total,
				"pk_customer":i.customer.pk,	
				"name_customer":i.customer.name
			}
			for i in cls.objects.filter(branch = branch, cancelled = False).order_by('-date')
		]

	@classmethod
	def delete_invoice(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"pk_invoice": None
		}
		if Employee.check_by_token(token=data["token"]):
			_invoice = cls.objects.filter(pk = data['pk_invoice']).first()
			if _invoice:
				employee = Employee.search_by_token(data['token'])
				#History_Invoice.create_history_invoice(_invoice, employee, 'Delete',employee.branch)
				serialized_invoice = serializers.serialize('json', [_invoice])
				invoice = json.loads(serialized_invoice)[0]
				HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.INVOICE,
					class_models_json=invoice,
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				_invoice.delete()
				result["code"] = 200
				result["status"] = "OK"
				result["message"] = "Success"
			else:
				result["message"] = "Factura no encontrada"
		return result

class MessageToInvoice(models.Model):
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)
	text = models.TextField()

	def __str__(self) -> str:
		return str(self.invoice.pk) + " | "+self.text

class NcToInvoice(models.Model):
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)

	def __str__(self) -> str:
		return str(self.invoice.pk)
	
class CreditNote(models.Model):
	nc_to_invoice = models.ForeignKey(NcToInvoice, on_delete = models.CASCADE)
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)

	def __str__(self) -> str:
		return "NC: "+str(self.nc_to_invoice.invoice.pk)+" | Invoice: "+str(self.invoice.pk)

class Details_Invoice(models.Model):
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	tax = models.FloatField()
	cost = models.FloatField()
	price = models.FloatField()
	ipo = models.FloatField()
	discount = models.FloatField()
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)
	product = models.ForeignKey(Product, on_delete = models.CASCADE, null=True, blank=True)
	tax_value = models.IntegerField(default = 0, null=True, blank = True)

	@classmethod
	def create_details(cls, data, invoice):
		result = False
		message = None
		try:
			_product = Product.objects.get(pk = data['pk'], branch = invoice.branch)
			details_invoice = cls(
				code = data['code'],
				name = data['product'],
				quantity = data['quantity'],
				tax = data['tax'],
				cost = data["cost"],
				price = data['price'],
				ipo = data['ipo'],
				discount = data['discount'],
				invoice = invoice,
				product = _product,
				tax_value = _product.tax.tax_num
			)
			details_invoice.save()
			result = True
			message = "Success"
			if result:
				if invoice.type_document != 99:
					value = Product.discount_product(data['pk'], invoice.branch, int(data['quantity']), invoice.employee)
					if not value['result']:
						result = value['result']
						message = value['message']
						invoice.delete()
						return {'result':result, 'message':message,'total':data['totalValue']}
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message,'total':data['totalValue']}

class Payment_Forms(models.Model):
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE)
	payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE, null=True, blank=True)
	payment_due_date = models.CharField(max_length = 12)
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)

	@classmethod
	def create_paymentform(cls, data, invoice:Invoice, employee):
		result = False
		message = None
		try:
			payment_form = cls.objects.filter(invoice=invoice).first()
			if not payment_form:
				_payment_form = Payment_Form.objects.filter(pk = data['payment_form']['paymentform']).first()
				_payment_method = Payment_Method.objects.filter(pk = data['payment_form']['paymentmethod']).first()
				payment_form = cls(
					payment_form = _payment_form,
					payment_method = _payment_method,
					payment_due_date = data['payment_form']['due_date'],
					invoice = invoice
				)
				payment_form.save()
				#if data['payment_form']['paymentform'] == 2:
				invoice.cancelled = False
				invoice.save()
				if data["type_document"] != 4:
					PaymentToPayInvoice.create_payment_to_pay(
						{
							"amount": 0, 
							"number": 1, 
							"nota": "Cuenta por cobrar a clientes",
							"expiration": data["expiration"],
							"term_payment": data["term_payment"]
						},
						invoice
					)
				result = True
				message = "Success"
				# else:
				# 	employee = Employee.objects.get(pk = employee.pk)
				# 	branch = employee.branch
				# 	serialized_product = serializers.serialize('json', [employee])
				# 	employee = json.loads(serialized_product)[0]['fields']
				# 	value = History_Invoice.create_history_invoice(data, employee, 'Created', branch)
				# 	result = value['result']
				# 	message = value['message']
			else:
				payment_form.payment_form = Payment_Form.objects.get(pk = data['payment_form']['paymentform'])
				try:
					payment_form.payment_method = Payment_Method.objects.get(pk = data['payment_form']['paymentmethod'])
				except Exception as e:
					print("Error in paymentMethod: "+str(e))
				payment_form.payment_due_date = data['payment_form']['due_date']
				payment_form.save()

				payment_to_pay = PaymentToPayInvoice.objects.filter(invoice = invoice).first()
				payment_to_pay.date = data["expiration"]
				payment_to_pay.term_payment = TermPayment.objects.filter(pk = data["term_payment"]).first()
				payment_to_pay.save()
				# if data['payment_form']['paymentform'] == 2:
				# 	invoice.cancelled = False
				# 	invoice.save()
				# 	_data = {
				# 		"pk_invoice": invoice.pk,
				# 		"amount":0,
				# 		"note":"There are no pass yet",
				# 		"pk_employee": employee.pk
				# 	}
				# 	Pass.create_pass(_data)
				# 	result = True
				# 	message = "Success"
				# else:
				employee = Employee.objects.get(pk = employee.pk)
				branch = employee.branch
				serialized_product = serializers.serialize('json', [employee])
				employee = json.loads(serialized_product)[0]['fields']
				value = History_Invoice.create_history_invoice(data, employee, 'Update', branch)
				result = value['result']
				message = value['message']

		except Exception as e:
			message = f"{e} - Error Payment Form"
		return {'result':result, 'message':message}

class PaymentToPayInvoice(models.Model): # Cuenta por cobrar
	number = models.IntegerField()
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)
	amount = models.FloatField()
	date = models.DateTimeField()
	note = models.TextField()
	employee = models.JSONField(null = True, blank = True)
	term_payment = models.ForeignKey(TermPayment, on_delete = models.CASCADE, null = True, blank = True)

	def get_state_payment_to_invoice(self):
		return "Cobrada" if self.amount >= self.invoice.total else "Por cobrar"

	@classmethod
	def create_payment_to_pay(cls, data, invoice:Invoice):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
		}
		employee = invoice.employee
		branch = employee.branch
		_payment_to_pay = cls.objects.filter(invoice = invoice).first()
		if _payment_to_pay:
			if _payment_to_pay.amount < invoice.total:
				if (float(data['amount']) + _payment_to_pay.amount) <= invoice.total and float(data['amount']) > 0:
					#if float(data['amount']) != _payment_to_pay.amount:
					_payment_to_pay.amount += float(data['amount'])
					if invoice.total - _payment_to_pay.amount <= 0:
						invoice.state_invoice = "Pagada"
						invoice.save()
					result["code"] = 200
					result["status"] = "OK"
					result["message"] = "Credit to the invoice was accepted"
					serialized_payment_to_pay = serializers.serialize('json', [_payment_to_pay])
					payment_to_pay = json.loads(serialized_payment_to_pay)[0]['fields']
					HistoryGeneral.create_history(
						action=HistoryGeneral.UPDATE,
						class_models=HistoryGeneral.PAYMENT_TO_PAY,
						class_models_json=payment_to_pay,
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
					#else:
					#	result["message"] = "Monto igual al anterior."
				else:
					result["message"] = "No puede pagar más que el total de la factura."
		else:
			_payment_to_pay = cls.objects.create(
				number = data["number"],
				invoice = invoice,
				amount = data['amount'],
				date = data["expiration"],
				note = data["nota"],
				term_payment = TermPayment.objects.filter(pk = data["term_payment"]).first()
			)
			result["code"] = 200
			result["status"] = "OK"
			result["message"] = f"Credit to the invoice {invoice.number} was created successfully"
			payment_to_pay = cls.objects.filter(invoice=invoice).first()
			serialized_payment_to_pay = serializers.serialize('json', [payment_to_pay])
			payment_to_pay = json.loads(serialized_payment_to_pay)[0]['fields']
			HistoryGeneral.create_history(
				action=HistoryGeneral.CREATED,
				class_models=HistoryGeneral.PAYMENT_TO_PAY,
				class_models_json=payment_to_pay,
				employee=employee.pk,
				username=employee.user_django.username,
				branch=employee.branch.pk
			)

		_payment_to_pay.save()
		if _payment_to_pay.amount == invoice.total:
			invoice.cancelled = True
			invoice.save()
			result["message"] = "The invoice has already been canceled"

		return result

class PaymentInvoice(models.Model): # pagos recibidos.
	number = models.IntegerField()
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE, null = True, blank = True)
	customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE, null=True, blank=True)
	bank = models.ForeignKey(Bank, on_delete = models.CASCADE, null=True, blank=True)
	amount = models.FloatField()
	imp_saldo_ant = models.FloatField(default=0)
	imp_saldo_insoluto = models.FloatField(default=0)
	date = models.DateTimeField()
	note = models.TextField()
	employee = models.JSONField(null = True, blank = True)
	conciliation = models.BooleanField(default=False)
	pdf = models.CharField(max_length=1024, null=True, blank=True)
	STATE = (
		("Timbrada", "Timbrada"),
		("No timbrada", "No timbrada"),
		("Cancelado", "Cancelado"),
		("Vigente", "Vigente"),
	)
	state = models.CharField(choices=STATE, max_length = 256, null = True, blank = True, default="No timbrada")
	STATE_EMAIL = (
		("Email enviado", "Email enviado"),
		("Email no enviado", "Email no enviado"),
	)
	state_email = models.CharField(choices=STATE_EMAIL, max_length = 256, null=True, blank=True, default="Email no enviado")
	
	no_cert_dig = models.CharField(max_length = 100, null=True, blank=True)
	cadena_original = models.CharField(max_length = 3024,null = True, blank = True)
	
	sello_cfdi = models.CharField(max_length = 2024,null = True, blank = True)
	no_cert_sat = models.CharField(max_length = 100, null=True, blank=True)
	UUID = models.CharField(max_length = 1024,null = True, blank = True)
	cufe = models.CharField(max_length = 1024,null = True, blank = True) # SatSeal Sello de SAT
	date_cert = models.CharField(max_length = 12, null=True, blank=True)
	status_file = models.TextField(null = True, blank = True)
	parcialidad = models.IntegerField(default=1)
	created = models.DateTimeField(null=True, blank=True)

	timbre_path = "media/complements/"

	def __str__(self) -> str:
		return str(self.number)

	@classmethod
	def create_payment(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				print(data)
				employee = Employee.search_by_token(data['token'])
				branch = employee.branch
				invoice = Invoice.objects.filter(pk = data["pkInvoice"]).first()
				_payment_invoice = cls.objects.filter(pk = int(data["pk"])).first()
				_payment_form = Payment_Form.objects.filter(pk = data["payment_form"]).first()
				bank = Bank.objects.filter(pk = data["bank"]).first()
				customer = Customer.objects.filter(pk = data["pk_customer"]).first()
				if not _payment_invoice:
					_payment_invoice = cls.objects.create(
						number = data["number"],
						invoice = invoice,
						customer = customer,
						payment_form = _payment_form,
						bank = bank,
						amount = float(data['totalValue']),
						date = data["date"],
						note = data["notas"],
						created = str(datetime.now())
					)
					from company.models import Consecutive
					Consecutive.consecutive_increment("ni", branch)
					result["code"] = 200
					result["status"] = "OK"
					result["message"] = "Success"
					
					PaymentToPayInvoice.create_payment_to_pay(
						{
							"amount": float(data['totalValue']),
						},
						invoice
					)
					_payment_invoice = cls.objects.filter(pk=_payment_invoice.pk).first()
					result["pk"] = _payment_invoice.pk
					serialized_payment_invoice = serializers.serialize('json', [_payment_invoice])
					payment_invoice = json.loads(serialized_payment_invoice)[0]['fields']
					HistoryGeneral.create_history(
						action=HistoryGeneral.CREATED,
						class_models=HistoryGeneral.PAYMENT_INVOICE,
						class_models_json=payment_invoice,
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
				else:
					_payment_invoice.invoice = invoice
					_payment_invoice.customer = customer
					_payment_invoice.payment_form = _payment_form
					_payment_invoice.bank = bank
					_payment_invoice.amount = float(data['totalValue'])
					_payment_invoice.date = data["date"]
					_payment_invoice.note = data["notas"]
					_payment_invoice.save()
					result["pk"] = _payment_invoice.pk
					result["code"] = 200
					result["status"] = "OK"
					result["message"] = "Success"
					PaymentToPayInvoice.create_payment_to_pay(
						{
							"amount": float(data['totalValue']),
						},
						invoice
					)

					serialized_payment_invoice = serializers.serialize('json', [cls.objects.filter(pk = int(data["pk"])).first()])
					payment_invoice = json.loads(serialized_payment_invoice)[0]['fields']
					HistoryGeneral.create_history(
						action=HistoryGeneral.UPDATE,
						class_models=HistoryGeneral.PAYMENT_INVOICE,
						class_models_json=payment_invoice,
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)

		except Exception as e:
			result["message"] = str(e)
		print(result)
		return result

	@classmethod
	def get_list_payment(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"data": []
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				for a in Invoice.objects.filter(branch = branch).order_by('-pk'):
					for i in cls.objects.filter(invoice=a).order_by("-pk"):
						payment_to_pay = PaymentToPayInvoice.objects.filter(invoice=i.invoice).first()
						result["data"].append(
							{
								"type_document":i.invoice.type_document,
								'pk_invoice': i.invoice.pk,
								'paid': Product.format_price(i.amount),
								'to_pay': Product.format_price(i.invoice.total - payment_to_pay.amount) if payment_to_pay else None,
								'cuenta': payment_to_pay.note,
								'number_invoice': i.invoice.number,
								'number': i.number,
								'date': str(i.date.date()),
								'name_customer': i.invoice.customer.name,
								'pk_customer': i.invoice.customer.pk,
								'total': Product.format_price(i.invoice.total),
								"state":i.state,
								"cancelled":i.invoice.cancelled,
								"annulled":i.invoice.annulled,
								"pk": i.pk,
								"note": i.note,
								"conciliation": i.conciliation,
								"pdf": i.pdf
							}
						)
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"

		except Exception as e:
			result['message'] = str(e)
		#print(result)
		return result
	
	@classmethod
	def get_payment(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"data": {}
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				payment_invoice = cls.objects.filter(pk = data["pk"]).first()
				payment_to_pay = PaymentToPayInvoice.objects.filter(invoice=payment_invoice.invoice).first()
				__company = json.loads(serializers.serialize('json', [payment_invoice.invoice.branch.company]))[0]['fields']
				__company["pk"] = payment_invoice.invoice.branch.company.pk
				__company['type_regime'] = json.loads(serializers.serialize('json', [payment_invoice.invoice.branch.company.type_regime]))[0]['fields']
				__company["address"] = str(payment_invoice.invoice.branch.company.address).split(",")
				__company["estado"] = payment_invoice.invoice.branch.company.municipality.state.name
				serialized_customer = serializers.serialize('json', [payment_invoice.invoice.customer])
				__customer = json.loads(serialized_customer)[0]['fields']
				__customer["pk"] = payment_invoice.invoice.customer.pk,
				__customer["code_postal"] = str(payment_invoice.invoice.customer.address).split(",")[0]
				__payment_form = json.loads(serializers.serialize('json', [payment_invoice.payment_form]))[0]['fields']
				__payment_form["pk"] = payment_invoice.payment_form.pk
				__payment_method_invoice = json.loads(serializers.serialize('json', [Payment_Forms.objects.get(invoice = payment_invoice.invoice).payment_method]))[0]['fields']
				__payment_form_invoice = json.loads(serializers.serialize('json', [Payment_Forms.objects.get(invoice = payment_invoice.invoice).payment_form]))[0]['fields']

				result["data"] = {
					"pk": payment_invoice.pk,
					"type_document":payment_invoice.invoice.type_document,
					'pk_invoice': payment_invoice.invoice.pk,
					'paid': payment_to_pay.amount if payment_to_pay else None,
					'to_pay': payment_invoice.invoice.total - payment_to_pay.amount if payment_to_pay else None,
					'number_invoice': payment_invoice.invoice.number,
					'number': payment_invoice.number,
					'date': str(payment_invoice.date.date()),
					"created": str(payment_invoice.created),
					'name_customer': payment_invoice.customer.name,
					'pk_customer': payment_invoice.customer.pk,
					'total': payment_invoice.invoice.total,
					"state":payment_invoice.state,
					"cancelled":payment_invoice.invoice.cancelled,
					"annulled":payment_invoice.invoice.annulled,
					"payment_form": payment_invoice.payment_form.pk,
					"bank": payment_invoice.bank.pk,
					"note": payment_invoice.note,
					"documentI": payment_invoice.customer.identification_number,
					'total_paid': payment_invoice.amount,
					"conciliation": payment_invoice.conciliation,
					"pdf": payment_invoice.pdf,
					"company": __company,
					"customer": __customer,
					"UUID": payment_invoice.UUID,
					"no_cert_dig": payment_invoice.no_cert_dig,
					"no_cert_sat": payment_invoice.no_cert_sat,
					"date_cert": payment_invoice.date_cert,
					"imp_saldo_ant": payment_invoice.imp_saldo_ant,
					"imp_saldo_insoluto": payment_invoice.imp_saldo_insoluto,
					"UUID_invoice": payment_invoice.invoice.UUID,
					"folio": str(payment_invoice.invoice.prefix)+"-"+str(payment_invoice.invoice.number),
					"parcialidad": payment_invoice.parcialidad,
					"payment_form": __payment_form,
					"payment_method_invoice": __payment_method_invoice,
					"payment_form_invoice": __payment_form_invoice
				}
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"

		except Exception as e:
			result['message'] = str(e)
		#print(result)
		return result
	
	@classmethod
	def delete_payment(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
		}
		if Employee.check_by_token(token=data["token"]):
			_payment_invoice = cls.objects.filter(pk = data['pk']).first()
			if _payment_invoice:
				employee = Employee.search_by_token(data['token'])
				#History_Invoice.create_history_invoice(_invoice_provider, employee, 'Delete',employee.branch)
				serialized_payment_invoice = serializers.serialize('json', [_payment_invoice])
				payment_invoice = json.loads(serialized_payment_invoice)[0]
				HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.PAYMENT_INVOICE,
					class_models_json=payment_invoice,
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				ppi = PaymentToPayInvoice.objects.filter(invoice=_payment_invoice.invoice).first()
				if ppi:
					ppi.amount -= _payment_invoice.amount
					ppi.save()
					__invoice = ppi.invoice
					if __invoice.total - ppi.amount > 0:
						__invoice.state_invoice = "Por cobrar"
						__invoice.save()
				_payment_invoice.delete()
				result["code"] = 200
				result["status"] = "OK"
				result["message"] = "Success"
			else:
				result["message"] = "Pago no encontrada"
		return result

class InvoiceFromTicket(models.Model):
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE, null = True, blank = True)
	period = models.CharField(max_length=50)
	month = models.CharField(max_length=50)


class TicketGeneral(models.Model):
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE, null = True, blank = True)
	invoice_from_ticket = models.ForeignKey(InvoiceFromTicket, on_delete = models.SET_NULL, null = True, blank = True)


class InvoiceFrequent(models.Model):
	date_from = models.DateField()
	date_to = models.DateField()
	frequent = models.IntegerField()
	observation = models.TextField()
	description = models.TextField()
	number_account = models.CharField(max_length=156)
	total = models.FloatField(null = True, blank = True)
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE)
	payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE)
	uso_cfdi = models.ForeignKey(CFDI, on_delete = models.CASCADE, null = True, blank = True)
	list_price = models.ForeignKey(List_Price, on_delete = models.CASCADE, related_name='list_price', null=True, blank=True)
	store = models.ForeignKey(Store, on_delete = models.CASCADE, related_name='store', null=True, blank=True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
	term_payment = models.ForeignKey(TermPayment, on_delete = models.CASCADE, null = True, blank = True)

	FV = "Factura de venta"
	FA = "Factura de arrendamiento"
	TYPE = (
		(FV, FV),
		(FA, FA),
	)
	type_invoice = models.TextField(choices=TYPE, default=FV)
	serie_folio = models.ForeignKey(SerieFolio, on_delete = models.CASCADE, null = True, blank = True)

	seller_info = models.ForeignKey(SellerInfo, on_delete = models.CASCADE, null=True, blank=True)
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE, null = True, blank = True)

	def __str__(self):
		return str(self.date_from)+" | "+str(self.date_to)
	
	@classmethod
	def create_invoice_frequent(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				print(data)
				employee = Employee.search_by_token(data['token'])
				invoice_frequent = InvoiceFrequent.objects.filter(pk = data["pk"]).first()
				if not invoice_frequent:
					invoice_frequent = InvoiceFrequent.objects.create(
						date_from = data["date_from"],
						date_to = data["date_to"],
						frequent = data["frequent"],
						observation = data["observation"],
						description = data["description"],
						number_account = data["number_account"],
						total = data["total"],
						payment_form = Payment_Form.objects.filter(pk = data["payment_form"]).first(),
						payment_method = Payment_Method.objects.filter(pk = data["payment_method"]).first(),
						uso_cfdi = CFDI.objects.filter(pk = data["uso_cfdi"]).first(),
						list_price = List_Price.objects.filter(pk = data["list_price"]).first(),
						store = Store.objects.filter(pk = data["store"]).first(),
						branch = employee.branch,
						customer = Customer.objects.filter(pk = data["customer"]).first(),
						term_payment = TermPayment.objects.filter(pk = data["term_payment"]).first(),
						type_invoice = data["type_invoice"],
						serie_folio = SerieFolio.objects.filter(pk = data["serie_folio"]).first(),
						#seller_info = SellerInfo.objects.filter(pk = data["seller_info"]).first(),
						employee = employee
					)
				else:
					invoice_frequent.date_from = data["date_from"]
					invoice_frequent.date_to = data["date_to"]
					invoice_frequent.frequent = data["frequent"]
					invoice_frequent.observation = data["observation"]
					invoice_frequent.description = data["description"]
					invoice_frequent.number_account = data["number_account"]
					invoice_frequent.total = data["total"]
					invoice_frequent.payment_form = Payment_Form.objects.filter(pk = data["payment_form"]).first()
					invoice_frequent.payment_method = Payment_Method.objects.filter(pk = data["payment_method"]).first()
					invoice_frequent.uso_cfdi = CFDI.objects.filter(pk = data["uso_cfdi"]).first()
					invoice_frequent.list_price = List_Price.objects.filter(pk = data["list_price"]).first()
					invoice_frequent.store = Store.objects.filter(pk = data["store"]).first()
					invoice_frequent.branch = employee.branch
					invoice_frequent.customer = Customer.objects.filter(pk = data["customer"]).first()
					invoice_frequent.term_payment = TermPayment.objects.filter(pk = data["term_payment"]).first()
					invoice_frequent.type_invoice = data["type_invoice"]
					invoice_frequent.serie_folio = SerieFolio.objects.filter(pk = data["serie_folio"]).first()
					#invoice_frequent.seller_info = SellerInfo.objects.filter(pk = data["seller_info"]).first()
					invoice_frequent.save()
				
				# buscamos los productos asociados y comparamos con los productos que vienen en la solicitud.
				# eliminar productos que ya no estan en uso y actualizar productos.
				for p in DetailsInvoiceFrequent.objects.filter(invoice=invoice_frequent):
					state = False
					for p2 in data["details"]:
						if p2["pk_item"] != 0:
							if p2["pk_item"] == p.pk:
								# actualizar producto.
								p.quantity = p2["quantity"]
								p.cost = p2["cost"]
								p.price = p2["price"]
								p.tax = p2["tax"]
								p.save()

								state = True
								break
					if not state:
						p.delete()
				# crear productos.
				result["pk_invoice"] = invoice_frequent.pk
				for i in data['details']:
					if i["pk_item"] == 0:
						DetailsInvoiceFrequent.create_details(i, invoice_frequent)

				result["code"] = 200
				result["message"] = "Success"
				result["status"] = "OK"

		except Exception as e:
			result['message'] = str(e)

		return result

	@classmethod
	def get_list_invoice_frequent(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"data": []
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				for _if in InvoiceFrequent.objects.filter(branch = branch).order_by("-id"):
					invoice_frequent_json = json.loads(serializers.serialize('json', [_if]))[0]["fields"]
					invoice_frequent_json["pk"] = _if.pk
					invoice_frequent_json["total"] = Product.format_price(_if.total)
					
					try:
						payment_form = json.loads(serializers.serialize('json', [_if.payment_form]))[0]["fields"]
						payment_form["pk"] = _if.payment_form.pk
						invoice_frequent_json["payment_form"] = payment_form
					except Exception as e:
						print("Error in payment_form invoice frequent")

					try:
						payment_method = json.loads(serializers.serialize('json', [_if.payment_method]))[0]["fields"]
						payment_method["pk"] = _if.payment_method.pk
						invoice_frequent_json["payment_method"] = payment_method
					except Exception as e:
						print("Error in payment_method invoice frequent")

					try:
						uso_cfdi = json.loads(serializers.serialize('json', [_if.uso_cfdi]))[0]["fields"]
						uso_cfdi["pk"] = _if.uso_cfdi.pk
						invoice_frequent_json["uso_cfdi"] = uso_cfdi
					except Exception as e:
						print("Error in uso_cfdi invoice frequent")

					try:
						list_price = json.loads(serializers.serialize('json', [_if.list_price]))[0]["fields"]
						list_price["pk"] = _if.list_price.pk
						invoice_frequent_json["list_price"] = list_price
					except Exception as e:
						print("Error in list_price invoice frequent")

					try:
						store = json.loads(serializers.serialize('json', [_if.store]))[0]["fields"]
						store["pk"] = _if.store.pk
						invoice_frequent_json["store"] = store
					except Exception as e:
						print("Error in store invoice frequent")

					try:
						branch = json.loads(serializers.serialize('json', [_if.branch]))[0]["fields"]
						branch["pk"] = _if.branch.pk
						invoice_frequent_json["branch"] = branch
					except Exception as e:
						print("Error in branch invoice frequent")

					try:
						customer = json.loads(serializers.serialize('json', [_if.customer]))[0]["fields"]
						customer["pk"] = _if.customer.pk
						invoice_frequent_json["customer"] = customer
					except Exception as e:
						print("Error in store customer frequent")

					try:
						term_payment = json.loads(serializers.serialize('json', [_if.term_payment]))[0]["fields"]
						term_payment["pk"] = str(_if.term_payment.pk)
						invoice_frequent_json["term_payment"] = term_payment
					except Exception as e:
						print("Error in term_payment invoice frequent")

					try:
						details = []
						for d in DetailsInvoiceFrequent.objects.filter(invoice=_if):
							detail = json.loads(serializers.serialize('json', [d]))[0]["fields"]
							detail["pk_item"] = d.pk
							detail["pk"] = d.product.pk
							details.append(detail)
						
						invoice_frequent_json["details"] = details
					except Exception as e:
						print("Error in details invoice frequent")
					
					result['data'].append(invoice_frequent_json)
				
				result["code"] = 200
				result["message"] = "Success"
				result["status"] = "OK"
		except Exception as e:
			result['message'] = str(e)

		return result

	@classmethod
	def get_invoice_frequent(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"data": {}
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				invoice_frequent = InvoiceFrequent.objects.filter(pk = data["pk"]).first()
				if invoice_frequent:
					invoice_frequent_json = json.loads(serializers.serialize('json', [invoice_frequent]))[0]["fields"]
					invoice_frequent_json["pk"] = invoice_frequent.pk
					
					try:
						payment_form = json.loads(serializers.serialize('json', [invoice_frequent.payment_form]))[0]["fields"]
						payment_form["pk"] = invoice_frequent.payment_form.pk
						invoice_frequent_json["payment_form"] = payment_form
					except Exception as e:
						print("Error in payment_form invoice frequent")
					
					try:
						payment_method = json.loads(serializers.serialize('json', [invoice_frequent.payment_method]))[0]["fields"]
						payment_method["pk"] = invoice_frequent.payment_method.pk
						invoice_frequent_json["payment_method"] = payment_method
					except Exception as e:
						print("Error in payment_method invoice frequent")

					try:
						uso_cfdi = json.loads(serializers.serialize('json', [invoice_frequent.uso_cfdi]))[0]["fields"]
						uso_cfdi["pk"] = invoice_frequent.uso_cfdi.pk
						invoice_frequent_json["uso_cfdi"] = uso_cfdi
					except Exception as e:
						print("Error in uso_cfdi invoice frequent")

					try:
						list_price = json.loads(serializers.serialize('json', [invoice_frequent.list_price]))[0]["fields"]
						list_price["pk"] = invoice_frequent.list_price.pk
						invoice_frequent_json["list_price"] = list_price
					except Exception as e:
						print("Error in list_price invoice frequent")

					try:
						store = json.loads(serializers.serialize('json', [invoice_frequent.store]))[0]["fields"]
						store["pk"] = invoice_frequent.store.pk
						invoice_frequent_json["store"] = store
					except Exception as e:
						print("Error in store invoice frequent")

					try:
						branch = json.loads(serializers.serialize('json', [invoice_frequent.branch]))[0]["fields"]
						branch["pk"] = invoice_frequent.branch.pk
						invoice_frequent_json["branch"] = branch
					except Exception as e:
						print("Error in branch invoice frequent")

					try:
						customer = json.loads(serializers.serialize('json', [invoice_frequent.customer]))[0]["fields"]
						customer["pk"] = invoice_frequent.customer.pk
						invoice_frequent_json["customer"] = customer
					except Exception as e:
						print("Error in customer invoice frequent")
					
					try:
						term_payment = json.loads(serializers.serialize('json', [invoice_frequent.term_payment]))[0]["fields"]
						term_payment["pk"] = invoice_frequent.term_payment.pk
						invoice_frequent_json["term_payment"] = term_payment
					except Exception as e:
						print("Error in term_payment invoice frequent")
					try:
						details = []
						for d in DetailsInvoiceFrequent.objects.filter(invoice=invoice_frequent):
							detail = json.loads(serializers.serialize('json', [d]))[0]["fields"]
							detail["pk_item"] = d.pk
							detail["pk"] = d.product.pk
							details.append(detail)
						
						invoice_frequent_json["details"] = details
					except Exception as e:
						print("Error in details invoice frequent")
					
					result["data"] = invoice_frequent_json

				result["code"] = 200
				result["message"] = "Success"
				result["status"] = "OK"
		except Exception as e:
			result['message'] = str(e)

		return result
	
	@classmethod
	def delete_invoice_frequent(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				invoice_frequent = InvoiceFrequent.objects.filter(pk = data["pk"]).first()
				invoice_frequent.delete()

				result["code"] = 200
				result["message"] = "Success"
				result["status"] = "OK"
		except Exception as e:
			result['message'] = str(e)

		return result
	
class DetailsInvoiceFrequent(models.Model):
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	tax = models.FloatField()
	cost = models.FloatField()
	price = models.FloatField()
	ipo = models.FloatField()
	discount = models.FloatField()
	invoice = models.ForeignKey(InvoiceFrequent, on_delete = models.CASCADE)
	product = models.ForeignKey(Product, on_delete = models.CASCADE, null=True, blank=True)
	tax_value = models.IntegerField(default = 0, null=True, blank = True)

	@classmethod
	def create_details(cls, data, invoice):
		result = False
		message = None
		try:
			print(data)
			_product = Product.objects.get(pk = data['pk'], branch = invoice.branch)
			details_invoice = cls(
				code = data['code'],
				name = data['product'],
				quantity = data['quantity'],
				tax = data['tax'],
				cost = data["cost"],
				price = data['price'],
				ipo = data['ipo'],
				discount = data['discount'],
				invoice = invoice,
				product = _product,
				tax_value = _product.tax.tax_num
			)
			details_invoice.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message,'total':data['totalValue']}

class Remission(models.Model):
	type_document = models.IntegerField()
	number = models.IntegerField()
	prefix = models.CharField(max_length = 7)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	date = models.CharField(max_length = 12)
	time = models.TimeField(auto_now_add = True)
	total = models.FloatField(null = True, blank = True)
	note = models.TextField(null = True, blank = True)
	customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
	cancelled = models.BooleanField(default = True)
	hidden = models.BooleanField(default = False)
	state = models.CharField(max_length = 70,null = True, blank = True)
	annulled = models.BooleanField(default = False)
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE, null = True, blank = True)
	STATE_EMAIL = (
		("Email enviado", "Email enviado"),
		("Email no enviado", "Email no enviado"),
	)
	state_email = models.CharField(choices=STATE_EMAIL, max_length = 256, null=True, blank=True, default="Email no enviado")
	pdf = models.CharField(max_length=1024, null=True, blank=True)
	status_file = models.TextField(null = True, blank = True)

	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE, null = True, blank = True)

	_path = "media/remission/"
	def __str__(self):
		return f"{self.prefix} - {self.number} by {self.branch.name}"

	@classmethod
	def send_email(cls, data):
		try:
			_remission = cls.objects.filter(pk = data["pk_invoice"]).first()
			if _remission.status_file == "Success":
				_pdf = "remission"+_remission.branch.company.documentI+str(_remission.prefix)+str(_remission.number)+".pdf"
				email_smtp = EmailSMTP.objects.all().last()
				email_send = MessageEmail.objects.filter(type_message=MessageEmail.SEND_FILE).first()
				send(
					email_smtp.email,
					email_smtp.password,
					data["email"],
					email_send.asunto,
					email_send.message,
					"",
					cls._path,
					_pdf,
					"",
					email_smtp.host,
					email_smtp.port
				)
				result = {
					"status": "OK",
					"code": 200,
					"message": "Email enviando correctamente."
				}
				_remission.state_email = "Email enviado"
				_remission.save()
			else:
				result = {
					"status": "Fail",
					"code": 400,
					"message": "Fallo al enviar documento."
				}
		except Exception as e:
			result = {
				"status": "Fail",
				"code": 400,
				"message": str(e)
			}
			_remission.state_email = str(e)
			_remission.save()
		return result

	@staticmethod
	def generate_qr_code(data,name_qr):
		result = False
		message = None
		try:
			qr = qrcode.QRCode(
			    version=1,
			    error_correction=qrcode.constants.ERROR_CORRECT_L,
			    box_size=10,
			    border=4,
			)
			qr.add_data(data)
			qr.make(fit=True)
			img = qr.make_image(fill_color="rgb(0, 0, 255)", back_color="rgb(255, 255, 255)")
			img = img.convert("RGBA")
			buffer = BytesIO()
			img.save(f"{env.URL_QR_IN_USE}{name_qr}.png")
		except Exception as e:
			message = str(e)
		return buffer

	@classmethod
	def generate_qr_code_view(cls, data):
		remission = Remission.get_remission(data['pk_invoice'])
		name_qr = f"{remission['prefix']}{remission['number']}"
		time = datetime.strptime(remission['time'], "%H:%M:%S.%f")
		remission_data = f"""Factura: {remission['prefix']}{remission['number']}\nEstablecimiento: {remission['branch']['name']}\nFecha: {remission['date']}\nHora: {time.strftime("%H:%M:%S")}\nTotal de la factura{remission['total']}\nNombre del Cliente: {remission['customer']['name']}"""
		qr_code_buffer = cls.generate_qr_code(remission_data, name_qr)
		return True

	@classmethod
	def get_selling_by_invoice(cls, data):
		return {'total':sum( int(json.loads(serializers.serialize('json', [i]))[0]['fields']['total']) for i in cls.objects.filter(type_document=data['type_document'], branch= Branch.objects.get(pk = data['pk_branch']), date = date.today()) )}

	@classmethod
	def get_selling_by_date(cls, data):
		branch = Branch.objects.get(pk=data['pk_branch'])
		start_date = datetime.strptime(data['date_start'], '%Y-%m-%d').date()
		end_date = date.today() + timedelta(days=1)
		totals_by_date = {str(start_date + timedelta(days=i)): 0 for i in range((end_date - start_date).days)}
		invoice = cls.objects.filter(branch=branch, date__range=(start_date, end_date))
		for i in invoice:
			invoice_date = str(i.date)
			total = int(i.total)
			totals_by_date[invoice_date] = totals_by_date.get(invoice_date, 0) + total
		return totals_by_date

	@classmethod
	def get_remission(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				_remission = cls.objects.get(pk = data['pk_invoice'])
				serialized_remission = serializers.serialize('json', [_remission])
				remission = json.loads(serialized_remission)[0]
				result["data"] = remission['fields']
				result["data"]['pk_invoice'] = data['pk_invoice']
				list_details = []
				for i in Details_Remission.objects.filter(remission = _remission):
					serialized_product = serializers.serialize('json', [i])
					product = json.loads(serialized_product)[0]['fields']
					product['subtotals'] = (product['price'] + product['ipo']) * product['quantity']
					product["pk_item"] = i.pk
					product["pk"] = i.product.pk

					product["description"] = i.product.description
					product["clave_uni_name"] = i.product.unit_measure.name
					product["clave_uni"] = i.product.unit_measure.clave
					product["clave_uni_type"] = i.product.unit_measure.tipo
					product["price_money"] = Product.format_price(i.product.price_1)

					list_details.append(product)
				result["data"]['details'] = list_details
				serialized_paymentform = serializers.serialize('json', [Payment_Forms_Remission.objects.get(remission = _remission)])
				result["data"]['payment_form'] = json.loads(serialized_paymentform)[0]['fields']
				result["data"]['company'] = json.loads(serializers.serialize('json', [_remission.branch.company]))[0]['fields']
				result["data"]['metod'] = "Crédito" if result["data"]['payment_form'] == 2 else "Efectivo"
				serialized_customer = serializers.serialize('json', [Customer.objects.get(pk = _remission.customer.pk)])
				result["data"]['customer'] = json.loads(serialized_customer)[0]['fields']
				_branch = Branch.objects.get(pk = _remission.branch.pk)
				branch = serializers.serialize('json', [_branch])
				result["data"]['branch'] = json.loads(branch)[0]['fields']
				resolution = {}
				try:
					resolution = serializers.serialize('json', [Resolution.objects.get(branch= _branch, type_document_id = result["data"]['type_document'])])
					result["data"]['resolution'] = json.loads(resolution)[0]['fields']
				except Exception as err:
					result["data"]['resolution'] = {}

				_emails = [_remission.customer.email]
				for p in Associate_Person.objects.filter(customer = _remission.customer):
					_emails.append(p.email)
				result["data"]["emails"] = _emails
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"
		except Exception as err2:
			result['message'] = str(err2)
		#print(result)
		return result

	@classmethod
	def annulled_remission(cls, data):
		result = False
		message = None
		try:
			invoice = cls.objects.get(pk = data['pk_invoice'], annulled = False)
			invoice.total = 0
			invoice.annulled = True
			invoice.state = "Factura Anulada."
			invoice.save()
			for i in Details_Remission.objects.filter(invoice = invoice):
				product = Product.objects.get(code = i.code)
				product.quantity += i.quantity
				product.save()
			result = True
			message = "Success"
			employee = Employee.objects.get(pk = data['pk_employee'])
			serialized_employee = serializers.serialize('json', [employee])
			employee = json.loads(serialized_employee)[0]['fields']
			serialized_invoice = serializers.serialize('json', [invoice])
			invoice = json.loads(serialized_invoice)[0]['fields']
			History_Invoice.create_history_invoice(invoice, employee, 'Annulled')
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

	@classmethod
	def annulled_remission_by_product(cls, data):
		result = False
		message = None
		try:
			invoice = cls.objects.get(pk=data['pk_invoice'], annulled=False)
			for detail_invoice in Details_Remission.objects.filter(invoice=invoice):
				product = Product.objects.get(code=data['code'])
				quantity = int(data['quantity'])
				if detail_invoice.quantity > 0:
					product.quantity += quantity
					total = round((detail_invoice.cost + detail_invoice.tax) * (detail_invoice.quantity - quantity))
					detail_invoice.price = total
					detail_invoice.quantity -= quantity
					invoice.note = ''
					product.save()
					detail_invoice.save()
					invoice.total = total
					invoice.save()
					data_invoice = Invoice.get_invoice(data['pk_invoice'])
					Credi_Note_Product(
	                	data_invoice,
	                	data['code'], data['quantity'], 1, "Devolucion de producto",
	                	Resolution.get_number(9)
	                ).Send()
					total_ncp = round((detail_invoice.cost + detail_invoice.tax) * quantity)
					quantity_send = Note_Credit_Product.create_nc_by_product(detail_invoice, quantity, total_ncp, invoice)
					invoice.note += f"Se aplico nota credito al producto {product.name} - Codigo {product.code} | Quitando {quantity_send['quantity_send']} productos\n"
					invoice.save()
					result = True
					message = "Success"
				else:
					message = "The product is already at zero"
		except cls.DoesNotExist:
			message = "Invoice does not exist"
		except Details_Remission.DoesNotExist:
			message = "Invoice details do not exist"
		except Product.DoesNotExist:
			message = "Product does not exist"
		except Exception as e:
			message = str(e)
		return {'result': result, 'message': message}

	@classmethod
	def get_list_remission(cls, data):
		result = {
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				for i in cls.objects.filter(branch = branch, type_document = data['type_document']).order_by('-pk'):
					_emails = [i.customer.email]
					for p in Associate_Person.objects.filter(customer = i.customer):
						_emails.append(p.email)
					result["data"].append(
						{
							"type_document":i.type_document,
							'pk_invoice': i.pk,
							'number': i.number,
							'prefix': i.prefix,
							'date': i.date,
							'name_client': i.customer.name,
							'total': Product.format_price(i.total),
							"state":i.state,
							"cancelled":i.cancelled,
							"annulled":i.annulled,
							"pdf": i.pdf,
							"emails": _emails
						}
					)
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"

		except Exception as e:
			result['message'] = str(e)
		return result

	@classmethod
	def create_remission(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"pk_invoice": None
		}
		total = 0
		try:
			if Employee.check_by_token(token=data["token"]):
				customer = Customer.objects.get(pk = data['pk_customer'])
				employee = Employee.search_by_token(data['token'])
				branch = employee.branch
				validate = License.validate_date(branch)
				if validate['result']:
					license = License.discount_license(branch)
					if license['result']:
						# validate remission create or modified
						remission = cls.objects.filter(pk=data["pk"]).first()
						if not remission:
							# create remission
							remission = cls(
								type_document = data['type_document'],
								number = data['number'],
								prefix = data['prefix'],
								branch = branch,
								date = data['date'],
								note = data['note'],
								customer = customer,
								hidden = True if data['type_document'] == 99 else False,
								state = data['state'],
								employee = employee
							)
							remission.save()

							from company.models import Consecutive
							Consecutive.consecutive_increment("rm", branch)

							result["pk_invoice"] = remission.pk
							state = True
							result['message'] = "Success"
							result['code'] = 200
							result['status'] = "OK"
							if state:
								for i in data['details']:
									value = Details_Remission.create_details(i, remission)
									if not value['result']:
										state = False
										result['message'] = value['message']
										break
									else:
										state = value['result']
										result['message'] = value['message']
										total += float(value['total'])

							if state:
								value = Payment_Forms_Remission.create_paymentform(data, remission, employee)
								state = value['result']
								result['message'] = value['message']
								if state:
									remission.total = total
									remission.save()
									values_wallet = {"pk_customer":customer.pk, 'amount_remission':total}
									#Wallet_Customer.update_coins(values_wallet)
									_data = {'type_document':data['type_document'], 'pk_branch':branch.pk}
									#Resolution.add_number(_data)
									#serialized_employee = serializers.serialize('json', [employee])
									#employee = json.loads(serialized_employee)[0]['fields']
									serialized_remission = serializers.serialize('json', [remission])
									_remission = json.loads(serialized_remission)[0]
									#History_Invoice.create_history_invoice(remission, employee, 'Created',branch)
									HistoryGeneral.create_history(
										action=HistoryGeneral.CREATED,
										class_models=HistoryGeneral.REMISSION,
										class_models_json=_remission,
										employee=employee.pk,
										username=employee.user_django.username,
										branch=employee.branch.pk
									)
								else:
									remission.delete()
							
							result['message'] = "Remission creada correctamente."
							result['code'] = 200
							result['status'] = "OK"
						else:
							# update invoice
							#print(data)
							remission.type_document = data['type_document']
							remission.number = data['number']
							remission.prefix = data['prefix']
							remission.branch = branch
							remission.date = data['date']
							remission.note = data['note']
							remission.customer = customer
							remission.hidden = True if data['type_document'] == 99 else False
							remission.state = data['state']
							remission.employee = employee
							remission.invoice = Invoice.objects.filter(pk=data["invoice"]).first()
							remission.save()

							# buscamos los productos asociados y comparamos con los productos que vienen en la solicitud.
							# eliminar productos que ya no estan en uso y actualizar productos.
							for p in Details_Remission.objects.filter(remission=remission):
								state = False
								for p2 in data["details"]:
									if p2["pk_item"] != 0:
										if p2["pk_item"] == p.pk:
											# actualizar producto.
											p.quantity = p2["quantity"]
											p.cost = p2["cost"]
											p.price = p2["price"]
											p.save()

											state = True
											break
								if not state:
									p.delete()
							# crear productos.
							result["pk_invoice"] = remission.pk
							state = True
							if state:
								for i in data['details']:
									if i["pk_item"] == 0:
										value = Details_Remission.create_details(i, remission)
										if not value['result']:
											state = False
											result['message'] = value['message']
											break
										else:
											state = value['result']
											result['message'] = value['message']
											total += float(value['total'])

							if state:
								value = Payment_Forms_Remission.create_paymentform(data, remission, employee)
								state = value['result']
								result['message'] = value['message']
								if state:
									remission.total = float(data["totalValue"])
									remission.save()
									values_wallet = {"pk_customer":customer.pk, 'amount_remission':total}
									#Wallet_Customer.update_coins(values_wallet)
									_data = {'type_document':data['type_document'], 'pk_branch':branch.pk}
									#Resolution.add_number(_data)
									#serialized_employee = serializers.serialize('json', [employee])
									#employee = json.loads(serialized_employee)[0]['fields']
									serialized_remission = serializers.serialize('json', [remission])
									_remission = json.loads(serialized_remission)[0]
									#History_Invoice.create_history_invoice(remission, employee, 'Updated',branch)
									HistoryGeneral.create_history(
										action=HistoryGeneral.UPDATE,
										class_models=HistoryGeneral.REMISSION,
										class_models_json=_remission,
										employee=employee.pk,
										username=employee.user_django.username,
										branch=employee.branch.pk
									)
							
							

							result['message'] = "Remission actualizada correctamente."
							result['code'] = 200
							result['status'] = "OK"
						
						try:
							_invoice_data = cls.get_remission({
								"token": data["token"],
								"pk_invoice": remission.pk
							})
							_name_file = "remission"+remission.branch.company.documentI+str(remission.prefix)+str(remission.number)+".pdf"
							_file_name_save = "remission"+remission.branch.company.documentI+str(remission.prefix)+str(remission.number)
							_invoice_data["data"]["path_dir"] = "media/remission/"
							Create_PDF_Invoice(_invoice_data["data"], "pdf_remission", _file_name_save)
							remission.status_file = "Success"
							remission.pdf = settings.URL_FILE+"media/remission/"+str(_name_file)
							remission.save()
						except Exception as epdf:
							remission.status_file = str(epdf)
							remission.save()
					else:
						result["message"] = license['message']
				else:
					result["message"] = validate['message']
		except Exception as e:
			result["message"] = str(e)
			print(e, 'Created Remission')
		return result

	@classmethod
	def get_list_remission_credit(cls, branch):
		return [
			{
				"pk_invoice" : i.pk,
				"number": i.number,
				"prefix": i.prefix,
				"date": i.date,
				"total": i.total,
				"pk_customer":i.customer.pk,	
				"name_customer":i.customer.name
			}
			for i in cls.objects.filter(branch = branch, cancelled = False).order_by('-date')
		]

	@classmethod
	def delete_remission(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"pk_invoice": None
		}
		if Employee.check_by_token(token=data["token"]):
			_remission = cls.objects.filter(pk = data['pk_invoice']).first()
			if _remission:
				employee = Employee.search_by_token(data['token'])
				#History_Invoice.create_history_invoice(_remission, employee, 'Delete',employee.branch)
				serialized_remission = serializers.serialize('json', [_remission])
				remission = json.loads(serialized_remission)[0]
				HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.REMISSION,
					class_models_json=remission,
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				_remission.delete()
				result["code"] = 200
				result["status"] = "OK"
				result["message"] = "Success"
			else:
				result["message"] = "Remision no encontrada"
		return result

class Details_Remission(models.Model):
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	tax = models.FloatField()
	cost = models.FloatField()
	price = models.FloatField()
	ipo = models.FloatField()
	discount = models.FloatField()
	remission = models.ForeignKey(Remission, on_delete = models.CASCADE)
	product = models.ForeignKey(Product, on_delete = models.CASCADE, null=True, blank=True)
	tax_value = models.IntegerField(default = 0, null=True, blank = True)

	@classmethod
	def create_details(cls, data, remission:Remission):
		result = False
		message = None
		try:
			_product = Product.objects.get(pk = data['pk'], branch = remission.branch)
			details_remission = cls(
				code = data['code'],
				name = data['product'],
				quantity = data['quantity'],
				tax = data['tax'],
				cost = data["cost"],
				price = data['price'],
				ipo = data['ipo'],
				discount = data['discount'],
				remission = remission,
				product = _product,
				tax_value = _product.tax.tax_num
			)
			details_remission.save()
			result = True
			message = "Success"
			if result:
				if remission.type_document != 99:
					value = Product.discount_product(data['pk'], remission.branch, int(data['quantity']), remission.employee)
					if not value['result']:
						result = value['result']
						message = value['message']
						remission.delete()
						return {'result':result, 'message':message,'total':data['totalValue']}
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message,'total':data['totalValue']}

class Payment_Forms_Remission(models.Model):
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE)
	payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE)
	payment_due_date = models.CharField(max_length = 12)
	remission = models.ForeignKey(Remission, on_delete = models.CASCADE)

	@classmethod
	def create_paymentform(cls, data, remission:Remission, employee):
		result = False
		message = None
		try:
			payment_form = cls.objects.filter(remission=remission).first()
			if not payment_form:
				payment_form = cls(
					payment_form = Payment_Form.objects.get(pk = data['payment_form']['paymentform']),
					payment_method = Payment_Method.objects.get(pk = data['payment_form']['paymentmethod']),
					payment_due_date = data['payment_form']['due_date'],
					remission = remission
				)
				payment_form.save()
				if data['payment_form']['paymentform'] == 2:
					remission.cancelled = False
					remission.save()
					_data = {
						"pk_invoice": remission.pk,
						"amount":0,
						"note":"There are no pass yet",
						"pk_employee": employee.pk
					}
					PassRemission.create_pass(_data)
					result = True
					message = "Success"
				else:
					employee = Employee.objects.get(pk = employee.pk)
					branch = employee.branch
					serialized_product = serializers.serialize('json', [employee])
					employee = json.loads(serialized_product)[0]['fields']
					value = History_Invoice.create_history_invoice(data, employee, 'Created', branch)
					result = value['result']
					message = value['message']
			else:
				payment_form.payment_form = Payment_Form.objects.get(pk = data['payment_form']['paymentform'])
				payment_form.payment_method = Payment_Method.objects.get(pk = data['payment_form']['paymentmethod'])
				payment_form.payment_due_date = data['payment_form']['due_date']
				payment_form.save()

				# if data['payment_form']['paymentform'] == 2:
				# 	invoice.cancelled = False
				# 	invoice.save()
				# 	_data = {
				# 		"pk_invoice": invoice.pk,
				# 		"amount":0,
				# 		"note":"There are no pass yet",
				# 		"pk_employee": employee.pk
				# 	}
				# 	Pass.create_pass(_data)
				# 	result = True
				# 	message = "Success"
				# else:
				employee = Employee.objects.get(pk = employee.pk)
				branch = employee.branch
				serialized_product = serializers.serialize('json', [employee])
				employee = json.loads(serialized_product)[0]['fields']
				value = History_Invoice.create_history_invoice(data, employee, 'Update', branch)
				result = value['result']
				message = value['message']

		except Exception as e:
			message = f"{e} - Error Payment Form"
		return {'result':result, 'message':message}

class PassRemission(models.Model):
	number_pass = models.IntegerField()
	remission = models.ForeignKey(Remission, on_delete = models.CASCADE)
	amount = models.FloatField()
	date = models.DateTimeField(auto_now_add = True)
	note = models.TextField()
	employee = models.JSONField(null = True, blank = True)


	@classmethod
	def create_pass(cls, data):
		try:
			number = len(cls.objects.all())
		except Exception as e:
			pass
		remission = Remission.objects.get(pk = data['pk_invoice'])
		result = False
		message = None
		employee = Employee.objects.get(pk = data['pk_employee'])
		branch = employee.branch
		try:
			_pass = cls.objects.get(remission = remission)
			if _pass.amount < remission.total:
				if float(data['amount']) <= (remission.total - _pass.amount) and float(data['amount']) > 0:
					_pass.amount += float(data['amount'])
					message = "Credit to the invoice was accepted"
					result = True
				else:
					message = "You cannot pay more than the total invoice"
		except cls.DoesNotExist as e:
			_pass = cls(
				number_pass = number if number > 0 else 1,
				remission = remission,
				amount = data['amount'],
				note = data['note']
			)
			message = f"Credit to the invoice {remission.number} was created successfully"
			result = True
		_pass.save()
		if _pass.amount == remission.total:
			remission.cancelled = True
			remission.save()
			message = "The invoice has already been canceled"

		serialized_remission = serializers.serialize('json', [remission])
		serialized_customer = serializers.serialize('json', [remission.customer])

		customer = json.loads(serialized_customer)[0]['fields']
		remission = json.loads(serialized_remission)[0]['fields']

		employee = serializers.serialize('json', [employee])

		if result:
			History_Pass.create_history_pass(remission, data['amount'], customer, data['note'], employee, branch)
		return {'result':True, 'message':message}

	@classmethod
	def cancel_all_invoices(cls, data):
		employee = Employee.objects.get(pk = data['pk_employee'])
		customer = Customer.objects.get(pk = data['pk_customer'])
		pk = customer.pk
		remission = Remission.objects.filter(branch= employee.branch, cancelled = False, customer = customer)
		total = 0
		result = False
		message = None
		amount = data['amount']
		branch = employee.branch
		for i in remission:
			total += i.total

		if total == amount:
			for i in remission:
				_pass = cls.objects.get(remission = i)
				_pass.amount = i.total
				_pass.save()
				i.cancelled = True
				i.save()
				result = True
				message = "Invoice paid"
		else:
			note = None
			for i in remission:
				if amount >= i.total:
					_pass = cls.objects.get(remission = i)
					_pass.amount = i.total
					amount -= i.total
					i.cancelled = True
					_pass.save()
					note = "Pago factura"
					serialized_remission = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.customer])
					customer = json.loads(serialized_customer)[0]['fields']
					_remission = json.loads(serialized_remission)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_remission, data['amount'], customer, note , __employee,branch)
				else:
					_pass = cls.objects.get(remission = i)
					_pass.amount += amount
					_pass.save()
					note = "Abona a la factura"
					serialized_remission = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.customer])
					customer = json.loads(serialized_customer)[0]['fields']
					_remission = json.loads(serialized_remission)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_remission, data['amount'], customer, note , __employee,branch)
					if not _pass.remission.cancelled:
						amount -= _pass.amount
						if amount <= 0:
							break
				i.save()
				result = True
				message = "Invoice paid"
		values = {"pk_customer": pk, "amount": amount}
		Wallet_Customer.update_wallet_customer(data)
		return {'result':result, 'message':message,"returned_value":amount}



class Service(models.Model):
	type_document = models.IntegerField()
	number = models.IntegerField()
	prefix = models.CharField(max_length = 7)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	date = models.CharField(max_length = 12)
	time = models.TimeField(auto_now_add = True)
	total = models.FloatField(null = True, blank = True)
	note = models.TextField(null = True, blank = True)
	customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
	cancelled = models.BooleanField(default = True)
	hidden = models.BooleanField(default = False)
	state = models.CharField(max_length = 70,null = True, blank = True)
	annulled = models.BooleanField(default = False)
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE, null = True, blank = True)
	assigned = models.IntegerField(default=0)
	STATE_EMAIL = (
		("Email enviado", "Email enviado"),
		("Email no enviado", "Email no enviado"),
	)
	state_email = models.CharField(choices=STATE_EMAIL, max_length = 256, null=True, blank=True, default="Email no enviado")
	pdf = models.CharField(max_length=1024, null=True, blank=True)
	status_file = models.TextField(null = True, blank = True)
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE, null = True, blank = True)
	remission = models.ForeignKey(Remission, on_delete = models.CASCADE, null = True, blank = True)

	_path = "media/service/"

	def __str__(self):
		return f"{self.prefix} - {self.number} by {self.branch.name}"

	@classmethod
	def send_email(cls, data):
		try:
			_service = cls.objects.filter(pk = data["pk_invoice"]).first()
			if _service.status_file == "Success":
				_pdf = "service"+_service.branch.company.documentI+str(_service.prefix)+str(_service.number)+".pdf"
				email_smtp = EmailSMTP.objects.all().last()
				email_send = MessageEmail.objects.filter(type_message=MessageEmail.SEND_FILE).first()
				send(
					email_smtp.email,
					email_smtp.password,
					data["email"],
					email_send.asunto,
					email_send.message,
					"",
					cls._path,
					_pdf,
					"",
					email_smtp.host,
					email_smtp.port
				)
				result = {
					"status": "OK",
					"code": 200,
					"message": "Email enviando correctamente."
				}
				_service.state_email = "Email enviado"
				_service.save()
			else:
				result = {
					"status": "Fail",
					"code": 400,
					"message": "Fallo al enviar documento."
				}
		except Exception as e:
			result = {
				"status": "Fail",
				"code": 400,
				"message": str(e)
			}
			_service.state_email = str(e)
			_service.save()
		return result

	@staticmethod
	def generate_qr_code(data,name_qr):
		result = False
		message = None
		try:
			qr = qrcode.QRCode(
			    version=1,
			    error_correction=qrcode.constants.ERROR_CORRECT_L,
			    box_size=10,
			    border=4,
			)
			qr.add_data(data)
			qr.make(fit=True)
			img = qr.make_image(fill_color="rgb(0, 0, 255)", back_color="rgb(255, 255, 255)")
			img = img.convert("RGBA")
			buffer = BytesIO()
			img.save(f"{env.URL_QR_IN_USE}{name_qr}.png")
		except Exception as e:
			message = str(e)
		return buffer

	@classmethod
	def generate_qr_code_view(cls, data):
		service = cls.get_service(data['pk_invoice'])
		name_qr = f"{service['prefix']}{service['number']}"
		time = datetime.strptime(service['time'], "%H:%M:%S.%f")
		service_data = f"""Factura: {service['prefix']}{service['number']}\nEstablecimiento: {service['branch']['name']}\nFecha: {service['date']}\nHora: {time.strftime("%H:%M:%S")}\nTotal de la factura{service['total']}\nNombre del Cliente: {service['customer']['name']}"""
		qr_code_buffer = cls.generate_qr_code(service_data, name_qr)
		return True

	@classmethod
	def get_selling_by_invoice(cls, data):
		return {'total':sum( int(json.loads(serializers.serialize('json', [i]))[0]['fields']['total']) for i in cls.objects.filter(type_document=data['type_document'], branch= Branch.objects.get(pk = data['pk_branch']), date = date.today()) )}

	@classmethod
	def get_selling_by_date(cls, data):
		branch = Branch.objects.get(pk=data['pk_branch'])
		start_date = datetime.strptime(data['date_start'], '%Y-%m-%d').date()
		end_date = date.today() + timedelta(days=1)
		totals_by_date = {str(start_date + timedelta(days=i)): 0 for i in range((end_date - start_date).days)}
		invoice = cls.objects.filter(branch=branch, date__range=(start_date, end_date))
		for i in invoice:
			invoice_date = str(i.date)
			total = int(i.total)
			totals_by_date[invoice_date] = totals_by_date.get(invoice_date, 0) + total
		return totals_by_date

	@classmethod
	def get_service(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				_service = cls.objects.get(pk = data['pk_invoice'])
				serialized_service = serializers.serialize('json', [_service])
				service = json.loads(serialized_service)[0]
				result["data"] = service['fields']
				result["data"]['pk_invoice'] = data['pk_invoice']
				list_details = []
				for i in Details_Service.objects.filter(service = _service):
					serialized_product = serializers.serialize('json', [i])
					product = json.loads(serialized_product)[0]['fields']
					product['subtotals'] = (product['price'] + product['ipo']) * product['quantity']
					product["pk_item"] = i.pk
					product["pk"] = i.product.pk

					product["description"] = i.product.description
					product["clave_uni_name"] = i.product.unit_measure.name
					product["clave_uni"] = i.product.unit_measure.clave
					product["clave_uni_type"] = i.product.unit_measure.tipo
					product["price_money"] = Product.format_price(i.product.price_1)

					list_details.append(product)
				result["data"]['details'] = list_details
				serialized_paymentform = serializers.serialize('json', [Payment_Forms_Service.objects.get(service = _service)])
				result["data"]['payment_form'] = json.loads(serialized_paymentform)[0]['fields']
				result["data"]['company'] = json.loads(serializers.serialize('json', [_service.branch.company]))[0]['fields']
				result["data"]['metod'] = "Crédito" if result["data"]['payment_form'] == 2 else "Efectivo"
				serialized_customer = serializers.serialize('json', [Customer.objects.get(pk = _service.customer.pk)])
				result["data"]['customer'] = json.loads(serialized_customer)[0]['fields']
				_branch = Branch.objects.get(pk = _service.branch.pk)
				branch = serializers.serialize('json', [_branch])
				result["data"]['branch'] = json.loads(branch)[0]['fields']
				_employee = Employee.objects.filter(pk = _service.assigned).first()
				result["data"]["pk_assigned"] = _employee.pk if _employee else ""
				result["data"]["name_assigned"] = _employee.user_django.username if _employee else ""
				resolution = {}
				try:
					resolution = serializers.serialize('json', [Resolution.objects.get(branch= _branch, type_document_id = result["data"]['type_document'])])
					result["data"]['resolution'] = json.loads(resolution)[0]['fields']
				except Exception as err:
					result["data"]['resolution'] = {}

				_emails = [_service.customer.email]
				for p in Associate_Person.objects.filter(customer = _service.customer):
					_emails.append(p.email)
				result["data"]["emails"] = _emails
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"
		except Exception as err2:
			result['message'] = str(err2)
		#print(result)
		return result

	@classmethod
	def get_list_service(cls, data):
		result = {
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				for i in cls.objects.filter(branch = branch, type_document = data['type_document']).order_by('-pk'):
					ep = Employee.objects.filter(pk = i.assigned).first()
					_emails = [i.customer.email]
					for p in Associate_Person.objects.filter(customer = i.customer):
						_emails.append(p.email)
					result["data"].append(
						{
							"type_document":i.type_document,
							'pk_invoice': i.pk,
							'number': i.number,
							'prefix': i.prefix,
							'date': i.date,
							'name_client': i.customer.name,
							'total': Product.format_price(i.total),
							"state":i.state,
							"cancelled":i.cancelled,
							"annulled":i.annulled,
							"assigned": ep.user_django.username if ep else "",
							"pdf": i.pdf,
							"emails":_emails
						}
					)
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"

		except Exception as e:
			result['message'] = str(e)
		#print(result)
		return result

	@classmethod
	def create_service(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"pk_invoice": None
		}
		total = 0
		#try:
		if Employee.check_by_token(token=data["token"]):
			customer = Customer.objects.get(pk = data['pk_customer'])
			employee = Employee.search_by_token(data['token'])
			branch = employee.branch
			validate = License.validate_date(branch)
			if validate['result']:
				license = License.discount_license(branch)
				if license['result']:
					# validate service create or modified
					service = cls.objects.filter(pk=data["pk"]).first()
					if not service:
						# create service
						service = cls(
							type_document = data['type_document'],
							number = data['number'],
							prefix = data['prefix'],
							branch = branch,
							date = data['date'],
							note = data['note'],
							customer = customer,
							hidden = True if data['type_document'] == 99 else False,
							state = data['state'],
							employee = employee,
							assigned = data["assigned"]
						)
						service.save()
						from company.models import Consecutive
						Consecutive.consecutive_increment("se", branch)
						result["pk_invoice"] = service.pk
						state = True
						result['message'] = "Success"
						result['code'] = 200
						result['status'] = "OK"
						if state:
							for i in data['details']:
								value = Details_Service.create_details(i, service)
								if not value['result']:
									state = False
									result['message'] = value['message']
									break
								else:
									state = value['result']
									result['message'] = value['message']
									total += float(value['total'])

						if state:
							value = Payment_Forms_Service.create_paymentform(data, service, employee)
							print(value)
							state = value['result']
							result['message'] = value['message']
							if state:
								service.total = total
								service.save()
								values_wallet = {"pk_customer":customer.pk, 'amount_service':total}
								#Wallet_Customer.update_coins(values_wallet)
								_data = {'type_document':data['type_document'], 'pk_branch':branch.pk}
								#Resolution.add_number(_data)
								#serialized_employee = serializers.serialize('json', [employee])
								#employee = json.loads(serialized_employee)[0]['fields']
								serialized_service = serializers.serialize('json', [service])
								_service = json.loads(serialized_service)[0]
								#History_Invoice.create_history_invoice(service, employee, 'Created',branch)
								HistoryGeneral.create_history(
									action=HistoryGeneral.CREATED,
									class_models=HistoryGeneral.SERVICE,
									class_models_json=_service,
									employee=employee.pk,
									username=employee.user_django.username,
									branch=employee.branch.pk
								)
							else:
								service.delete()

						result['message'] = "Servicio creado correctamente."
					else:
						# update invoice
						#print(data)
						service.type_document = data['type_document']
						service.number = data['number']
						service.prefix = data['prefix']
						service.branch = branch
						service.date = data['date']
						service.note = data['note']
						service.customer = customer
						service.hidden = True if data['type_document'] == 99 else False
						service.state = data['state']
						service.employee = employee
						service.assigned = data["assigned"]
						service.invoice = Invoice.objects.filter(pk=data["invoice"]).first()
						service.remission = Remission.objects.filter(pk=data["remission"]).first()
						service.save()

						# buscamos los productos asociados y comparamos con los productos que vienen en la solicitud.
						# eliminar productos que ya no estan en uso y actualizar productos.
						for p in Details_Service.objects.filter(service=service):
							state = False
							for p2 in data["details"]:
								if p2["pk_item"] != 0:
									if p2["pk_item"] == p.pk:
										# actualizar producto.
										p.quantity = p2["quantity"]
										p.cost = p2["cost"]
										p.price = p2["price"]
										p.save()

										state = True
										break
							if not state:
								p.delete()
						# crear productos.
						result["pk_invoice"] = service.pk
						state = True
						if state:
							for i in data['details']:
								if i["pk_item"] == 0:
									value = Details_Service.create_details(i, service)
									if not value['result']:
										state = False
										result['message'] = value['message']
										break
									else:
										state = value['result']
										result['message'] = value['message']
										total += float(value['total'])

						if state:
							value = Payment_Forms_Service.create_paymentform(data, service, employee)
							state = value['result']
							result['message'] = value['message']
							if state:
								service.total = float(data["totalValue"])
								service.save()
								values_wallet = {"pk_customer":customer.pk, 'amount_service':total}
								#Wallet_Customer.update_coins(values_wallet)
								_data = {'type_document':data['type_document'], 'pk_branch':branch.pk}
								#Resolution.add_number(_data)
								#serialized_employee = serializers.serialize('json', [employee])
								#employee = json.loads(serialized_employee)[0]['fields']
								serialized_service = serializers.serialize('json', [service])
								_service = json.loads(serialized_service)[0]
								#History_Invoice.create_history_invoice(service, employee, 'Created',branch)
								HistoryGeneral.create_history(
									action=HistoryGeneral.UPDATE,
									class_models=HistoryGeneral.SERVICE,
									class_models_json=_service,
									employee=employee.pk,
									username=employee.user_django.username,
									branch=employee.branch.pk
								)
						
						result['message'] = "Servicio actualizado correctamente."
					
					try:
						_invoice_data = cls.get_service({
							"token": data["token"],
							"pk_invoice": service.pk
						})
						_name_file = "service"+service.branch.company.documentI+str(service.prefix)+str(service.number)+".xml"
						_file_name_save = "service"+service.branch.company.documentI+str(service.prefix)+str(service.number)
						_invoice_data["data"]["path_dir"] = "media/service/"
						Create_PDF_Invoice(_invoice_data["data"], "pdf_service", _file_name_save)
						service.status_file = "Success"
						service.pdf = settings.URL_FILE+"media/service/"+str(_name_file).replace("xml", "pdf")
						service.save()
					except Exception as epdf:
						service.status_file = str(epdf)
						service.save()

					result['code'] = 200
					result['status'] = "OK"
				else:
					result["message"] = license['message']
			else:
				result["message"] = validate['message']
		#except Exception as e:
		#	result["message"] = str(e)
		#	print(e, 'Created Service')
		return result

	@classmethod
	def get_list_service_credit(cls, branch):
		return [
			{
				"pk_invoice" : i.pk,
				"number": i.number,
				"prefix": i.prefix,
				"date": i.date,
				"total": i.total,
				"pk_customer":i.customer.pk,	
				"name_customer":i.customer.name
			}
			for i in cls.objects.filter(branch = branch, cancelled = False).order_by('-date')
		]

	@classmethod
	def delete_service(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"pk_invoice": None
		}
		if Employee.check_by_token(token=data["token"]):
			_service = cls.objects.filter(pk = data['pk_invoice']).first()
			if _service:
				employee = Employee.search_by_token(data['token'])
				#History_Invoice.create_history_invoice(_service, employee, 'Delete',employee.branch)
				serialized_service = serializers.serialize('json', [_service])
				service = json.loads(serialized_service)[0]
				HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.SERVICE,
					class_models_json=service,
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				_service.delete()
				result["code"] = 200
				result["status"] = "OK"
				result["message"] = "Success"
			else:
				result["message"] = "Servicio no encontrada"
		return result

class Details_Service(models.Model):
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	tax = models.FloatField()
	cost = models.FloatField()
	price = models.FloatField()
	ipo = models.FloatField()
	discount = models.FloatField()
	service = models.ForeignKey(Service, on_delete = models.CASCADE)
	product = models.ForeignKey(Product, on_delete = models.CASCADE, null=True, blank=True)
	tax_value = models.IntegerField(default = 0, null=True, blank = True)

	@classmethod
	def create_details(cls, data, service:Service):
		result = False
		message = None
		try:
			product = Product.objects.get(pk = data['pk'], branch = service.branch)
			details_service = cls(
				code = data['code'],
				name = data['product'],
				quantity = data['quantity'],
				tax = data['tax'],
				cost = data["cost"],
				price = data['price'],
				ipo = data['ipo'],
				discount = data['discount'],
				service = service,
				product = product,
				tax_value = product.tax.tax_num
			)
			details_service.save()
			result = True
			message = "Success"
			if result:
				if service.type_document != 99:
					value = Product.discount_product(data['pk'], service.branch, int(data['quantity']), service.employee)
					if not value['result']:
						result = value['result']
						message = value['message']
						service.delete()
						return {'result':result, 'message':message,'total':data['totalValue']}
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message,'total':data['totalValue']}

class Payment_Forms_Service(models.Model):
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE)
	payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE)
	payment_due_date = models.CharField(max_length = 12)
	service = models.ForeignKey(Service, on_delete = models.CASCADE)

	@classmethod
	def create_paymentform(cls, data, service:Service, employee):
		result = False
		message = None
		try:
			payment_form = cls.objects.filter(service=service).first()
			if not payment_form:
				payment_form = cls(
					payment_form = Payment_Form.objects.get(pk = data['payment_form']['paymentform']),
					payment_method = Payment_Method.objects.get(pk = data['payment_form']['paymentmethod']),
					payment_due_date = data['payment_form']['due_date'],
					service = service
				)
				payment_form.save()
				if data['payment_form']['paymentform'] == 2:
					service.cancelled = False
					service.save()
					_data = {
						"pk_invoice": service.pk,
						"amount":0,
						"note":"There are no pass yet",
						"pk_employee": employee.pk
					}
					PassService.create_pass(_data)
					result = True
					message = "Success"
				else:
					employee = Employee.objects.get(pk = employee.pk)
					branch = employee.branch
					serialized_product = serializers.serialize('json', [employee])
					employee = json.loads(serialized_product)[0]['fields']
					value = History_Invoice.create_history_invoice(data, employee, 'Created', branch)
					result = value['result']
					message = value['message']
			else:
				payment_form.payment_form = Payment_Form.objects.get(pk = data['payment_form']['paymentform'])
				payment_form.payment_method = Payment_Method.objects.get(pk = data['payment_form']['paymentmethod'])
				payment_form.payment_due_date = data['payment_form']['due_date']
				payment_form.save()

				# if data['payment_form']['paymentform'] == 2:
				# 	invoice.cancelled = False
				# 	invoice.save()
				# 	_data = {
				# 		"pk_invoice": invoice.pk,
				# 		"amount":0,
				# 		"note":"There are no pass yet",
				# 		"pk_employee": employee.pk
				# 	}
				# 	Pass.create_pass(_data)
				# 	result = True
				# 	message = "Success"
				# else:
				employee = Employee.objects.get(pk = employee.pk)
				branch = employee.branch
				serialized_product = serializers.serialize('json', [employee])
				employee = json.loads(serialized_product)[0]['fields']
				value = History_Invoice.create_history_invoice(data, employee, 'Update', branch)
				result = value['result']
				message = value['message']

		except Exception as e:
			message = f"{e} - Error Payment Form"
		return {'result':result, 'message':message}

class PassService(models.Model):
	number_pass = models.IntegerField()
	service = models.ForeignKey(Service, on_delete = models.CASCADE)
	amount = models.FloatField()
	date = models.DateTimeField(auto_now_add = True)
	note = models.TextField()
	employee = models.JSONField(null = True, blank = True)


	@classmethod
	def create_pass(cls, data):
		try:
			number = len(cls.objects.all())
		except Exception as e:
			pass
		service = Service.objects.get(pk = data['pk_invoice'])
		result = False
		message = None
		employee = Employee.objects.get(pk = data['pk_employee'])
		branch = employee.branch
		try:
			_pass = cls.objects.get(service = service)
			if _pass.amount < service.total:
				if float(data['amount']) <= (service.total - _pass.amount) and float(data['amount']) > 0:
					_pass.amount += float(data['amount'])
					message = "Credit to the service was accepted"
					result = True
				else:
					message = "You cannot pay more than the total service"
		except cls.DoesNotExist as e:
			_pass = cls(
				number_pass = number if number > 0 else 1,
				service = service,
				amount = data['amount'],
				note = data['note']
			)
			message = f"Credit to the service {service.number} was created successfully"
			result = True
		_pass.save()
		if _pass.amount == service.total:
			service.cancelled = True
			service.save()
			message = "The service has already been canceled"

		serialized_service = serializers.serialize('json', [service])
		serialized_customer = serializers.serialize('json', [service.customer])

		customer = json.loads(serialized_customer)[0]['fields']
		service = json.loads(serialized_service)[0]['fields']

		employee = serializers.serialize('json', [employee])

		if result:
			History_Pass.create_history_pass(service, data['amount'], customer, data['note'], employee, branch)
		return {'result':True, 'message':message}

	@classmethod
	def cancel_all_invoices(cls, data):
		employee = Employee.objects.get(pk = data['pk_employee'])
		customer = Customer.objects.get(pk = data['pk_customer'])
		pk = customer.pk
		service = Service.objects.filter(branch= employee.branch, cancelled = False, customer = customer)
		total = 0
		result = False
		message = None
		amount = data['amount']
		branch = employee.branch
		for i in service:
			total += i.total

		if total == amount:
			for i in service:
				_pass = cls.objects.get(service = i)
				_pass.amount = i.total
				_pass.save()
				i.cancelled = True
				i.save()
				result = True
				message = "service paid"
		else:
			note = None
			for i in service:
				if amount >= i.total:
					_pass = cls.objects.get(service = i)
					_pass.amount = i.total
					amount -= i.total
					i.cancelled = True
					_pass.save()
					note = "Pago service"
					serialized_service = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.customer])
					customer = json.loads(serialized_customer)[0]['fields']
					_service = json.loads(serialized_service)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_service, data['amount'], customer, note , __employee,branch)
				else:
					_pass = cls.objects.get(service = i)
					_pass.amount += amount
					_pass.save()
					note = "Abona al service"
					serialized_service = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.customer])
					customer = json.loads(serialized_customer)[0]['fields']
					_service = json.loads(serialized_service)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_service, data['amount'], customer, note , __employee,branch)
					if not _pass.service.cancelled:
						amount -= _pass.amount
						if amount <= 0:
							break
				i.save()
				result = True
				message = "Service paid"
		values = {"pk_customer": pk, "amount": amount}
		Wallet_Customer.update_wallet_customer(data)
		return {'result':result, 'message':message,"returned_value":amount}



class Cotization(models.Model):
	type_document = models.IntegerField()
	number = models.IntegerField()
	prefix = models.CharField(max_length = 7)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	date = models.CharField(max_length = 12)
	time = models.TimeField(auto_now_add = True)
	total = models.FloatField(null = True, blank = True)
	note = models.TextField(null = True, blank = True)
	customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
	cancelled = models.BooleanField(default = True)
	hidden = models.BooleanField(default = False)
	state = models.CharField(max_length = 70,null = True, blank = True)
	annulled = models.BooleanField(default = False)
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE, null = True, blank = True)
	STATE_EMAIL = (
		("Email enviado", "Email enviado"),
		("Email no enviado", "Email no enviado"),
	)
	state_email = models.CharField(choices=STATE_EMAIL, max_length = 256, null=True, blank=True, default="Email no enviado")
	pdf = models.CharField(max_length=1024, null=True, blank=True)
	status_file = models.TextField(null = True, blank = True)
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE, null = True, blank = True)
	remission = models.ForeignKey(Remission, on_delete = models.CASCADE, null = True, blank = True)

	_path = "media/cotization/"

	def __str__(self):
		return f"{self.prefix} - {self.number} by {self.branch.name}"

	@classmethod
	def send_email(cls, data):
		try:
			_cotization = cls.objects.filter(pk = data["pk_invoice"]).first()
			if _cotization.status_file == "Success":
				_pdf = "cotization"+_cotization.branch.company.documentI+str(_cotization.prefix)+str(_cotization.number)+".pdf"
				email_smtp = EmailSMTP.objects.all().last()
				email_send = MessageEmail.objects.filter(type_message=MessageEmail.SEND_FILE).first()
				send(
					email_smtp.email,
					email_smtp.password,
					data["email"],
					email_send.asunto,
					email_send.message,
					"",
					cls._path,
					_pdf,
					"",
					email_smtp.host,
					email_smtp.port
				)
				result = {
					"status": "OK",
					"code": 200,
					"message": "Email enviando correctamente."
				}
				_cotization.state_email = "Email enviado"
				_cotization.save()
			else:
				result = {
					"status": "Fail",
					"code": 400,
					"message": "Fallo al enviar documento."
				}
		except Exception as e:
			result = {
				"status": "Fail",
				"code": 400,
				"message": str(e)
			}
			_cotization.state_email = str(e)
			_cotization.save()
		return result

	@staticmethod
	def generate_qr_code(data,name_qr):
		result = False
		message = None
		try:
			qr = qrcode.QRCode(
			    version=1,
			    error_correction=qrcode.constants.ERROR_CORRECT_L,
			    box_size=10,
			    border=4,
			)
			qr.add_data(data)
			qr.make(fit=True)
			img = qr.make_image(fill_color="rgb(0, 0, 255)", back_color="rgb(255, 255, 255)")
			img = img.convert("RGBA")
			buffer = BytesIO()
			img.save(f"{env.URL_QR_IN_USE}{name_qr}.png")
		except Exception as e:
			message = str(e)
		return buffer

	@classmethod
	def generate_qr_code_view(cls, data):
		cotization = Cotization.get_cotization(data['pk_invoice'])
		name_qr = f"{cotization['prefix']}{cotization['number']}"
		time = datetime.strptime(cotization['time'], "%H:%M:%S.%f")
		cotization_data = f"""Factura: {cotization['prefix']}{cotization['number']}\nEstablecimiento: {cotization['branch']['name']}\nFecha: {cotization['date']}\nHora: {time.strftime("%H:%M:%S")}\nTotal de la factura{cotization['total']}\nNombre del Cliente: {cotization['customer']['name']}"""
		qr_code_buffer = cls.generate_qr_code(cotization_data, name_qr)
		return True

	@classmethod
	def get_selling_by_invoice(cls, data):
		return {'total':sum( int(json.loads(serializers.serialize('json', [i]))[0]['fields']['total']) for i in cls.objects.filter(type_document=data['type_document'], branch= Branch.objects.get(pk = data['pk_branch']), date = date.today()) )}

	@classmethod
	def get_selling_by_date(cls, data):
		branch = Branch.objects.get(pk=data['pk_branch'])
		start_date = datetime.strptime(data['date_start'], '%Y-%m-%d').date()
		end_date = date.today() + timedelta(days=1)
		totals_by_date = {str(start_date + timedelta(days=i)): 0 for i in range((end_date - start_date).days)}
		cotization = cls.objects.filter(branch=branch, date__range=(start_date, end_date))
		for i in cotization:
			cotization_date = str(i.date)
			total = int(i.total)
			totals_by_date[cotization_date] = totals_by_date.get(cotization_date, 0) + total
		return totals_by_date

	@classmethod
	def get_cotization(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				_cotization = cls.objects.get(pk = data['pk_invoice'])
				serialized_cotization = serializers.serialize('json', [_cotization])
				cotization = json.loads(serialized_cotization)[0]
				result["data"] = cotization['fields']
				result["data"]['pk_invoice'] = data['pk_invoice']
				list_details = []
				for i in Details_Cotization.objects.filter(cotization = _cotization):
					serialized_product = serializers.serialize('json', [i])
					product = json.loads(serialized_product)[0]['fields']
					product['subtotals'] = (product['price'] + product['ipo']) * product['quantity']
					product["pk_item"] = i.pk
					product["pk"] = i.product.pk

					product["description"] = i.product.description
					product["clave_uni_name"] = i.product.unit_measure.name
					product["clave_uni"] = i.product.unit_measure.clave
					product["clave_uni_type"] = i.product.unit_measure.tipo
					product["price_money"] = Product.format_price(i.product.price_1)

					list_details.append(product)
				result["data"]['details'] = list_details
				serialized_paymentform = serializers.serialize('json', [Payment_Forms_Cotization.objects.get(cotization = _cotization)])
				result["data"]['payment_form'] = json.loads(serialized_paymentform)[0]['fields']
				result["data"]['company'] = json.loads(serializers.serialize('json', [_cotization.branch.company]))[0]['fields']
				result["data"]['metod'] = "Crédito" if result["data"]['payment_form'] == 2 else "Efectivo"
				serialized_customer = serializers.serialize('json', [Customer.objects.get(pk = _cotization.customer.pk)])
				result["data"]['customer'] = json.loads(serialized_customer)[0]['fields']
				_branch = Branch.objects.get(pk = _cotization.branch.pk)
				branch = serializers.serialize('json', [_branch])
				result["data"]['branch'] = json.loads(branch)[0]['fields']
				resolution = {}
				try:
					resolution = serializers.serialize('json', [Resolution.objects.get(branch= _branch, type_document_id = result["data"]['type_document'])])
					result["data"]['resolution'] = json.loads(resolution)[0]['fields']
				except Exception as err:
					result["data"]['resolution'] = {}
				
				_emails = [_cotization.customer.email]
				for p in Associate_Person.objects.filter(customer = _cotization.customer):
					_emails.append(p.email)
				result["data"]["emails"] = _emails
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"
		except Exception as err2:
			result['message'] = str(err2)
		#print(result)
		return result

	@classmethod
	def annulled_cotization(cls, data):
		result = False
		message = None
		try:
			cotization = cls.objects.get(pk = data['pk_invoice'], annulled = False)
			cotization.total = 0
			cotization.annulled = True
			cotization.state = "Factura Anulada."
			cotization.save()
			for i in Details_Cotization.objects.filter(cotization = cotization):
				product = Product.objects.get(code = i.code)
				product.quantity += i.quantity
				product.save()
			result = True
			message = "Success"
			employee = Employee.objects.get(pk = data['pk_employee'])
			serialized_employee = serializers.serialize('json', [employee])
			employee = json.loads(serialized_employee)[0]['fields']
			serialized_cotization = serializers.serialize('json', [cotization])
			cotization = json.loads(serialized_cotization)[0]['fields']
			History_Invoice.create_history_invoice(cotization, employee, 'Annulled')
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

	@classmethod
	def annulled_cotization_by_product(cls, data):
		result = False
		message = None
		try:
			cotization = cls.objects.get(pk=data['pk_invoice'], annulled=False)
			for detail_cotization in Details_Cotization.objects.filter(cotization=cotization):
				product = Product.objects.get(code=data['code'])
				quantity = int(data['quantity'])
				if detail_cotization.quantity > 0:
					product.quantity += quantity
					total = round((detail_cotization.cost + detail_cotization.tax) * (detail_cotization.quantity - quantity))
					detail_cotization.price = total
					detail_cotization.quantity -= quantity
					cotization.note = ''
					product.save()
					detail_cotization.save()
					cotization.total = total
					cotization.save()
					data_cotization = Cotization.get_cotization(data['pk_invoice'])
					Credi_Note_Product(
	                	data_cotization,
	                	data['code'], data['quantity'], 1, "Devolucion de producto",
	                	Resolution.get_number(9)
	                ).Send()
					total_ncp = round((detail_cotization.cost + detail_cotization.tax) * quantity)
					quantity_send = Note_Credit_Product.create_nc_by_product(detail_cotization, quantity, total_ncp, cotization)
					cotization.note += f"Se aplico nota credito al producto {product.name} - Codigo {product.code} | Quitando {quantity_send['quantity_send']} productos\n"
					cotization.save()
					result = True
					message = "Success"
				else:
					message = "The product is already at zero"
		except cls.DoesNotExist:
			message = "Cotization does not exist"
		except Details_Cotization.DoesNotExist:
			message = "Cotization details do not exist"
		except Product.DoesNotExist:
			message = "Product does not exist"
		except Exception as e:
			message = str(e)
		return {'result': result, 'message': message}

	@classmethod
	def get_list_cotization(cls, data):
		result = {
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				for i in cls.objects.filter(branch = branch, type_document = data['type_document']).order_by('-pk'):
					_emails = [i.customer.email]
					for p in Associate_Person.objects.filter(customer = i.customer):
						_emails.append(p.email)
					result["data"].append(
						{
							"type_document":i.type_document,
							'pk_invoice': i.pk,
							'number': i.number,
							'prefix': i.prefix,
							'date': i.date,
							'name_client': i.customer.name,
							'total': Product.format_price(i.total),
							"state":i.state,
							"cancelled":i.cancelled,
							"annulled":i.annulled,
							"pdf": i.pdf,
							"emails": _emails
						}	
					)
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"

		except Exception as e:
			result['message'] = str(e)
		#print(result)
		return result

	@classmethod
	def create_cotization(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"pk_invoice": None
		}
		total = 0
		try:
			if Employee.check_by_token(token=data["token"]):
				customer = Customer.objects.get(pk = data['pk_customer'])
				employee = Employee.search_by_token(data['token'])
				branch = employee.branch
				validate = License.validate_date(branch)
				if validate['result']:
					license = License.discount_license(branch)
					if license['result']:
						# validate cotization create or modified
						cotization = cls.objects.filter(pk=data["pk"]).first()
						if not cotization:
							# create cotization
							cotization = cls(
								type_document = data['type_document'],
								number = data['number'],
								prefix = data['prefix'],
								branch = branch,
								date = data['date'],
								note = data['note'],
								customer = customer,
								hidden = True if data['type_document'] == 99 else False,
								state = data['state'],
								employee = employee
							)
							cotization.save()
							from company.models import Consecutive
							Consecutive.consecutive_increment("ct", branch)
							result["pk_invoice"] = cotization.pk
							state = True
							result['message'] = "Success"
							result['code'] = 200
							result['status'] = "OK"
							if state:
								for i in data['details']:
									value = Details_Cotization.create_details(i, cotization)
									if not value['result']:
										state = False
										result['message'] = value['message']
										break
									else:
										state = value['result']
										result['message'] = value['message']
										total += float(value['total'])

							if state:
								value = Payment_Forms_Cotization.create_paymentform(data, cotization, employee)
								state = value['result']
								result['message'] = value['message']
								if state:
									cotization.total = total
									cotization.save()
									values_wallet = {"pk_customer":customer.pk, 'amount_cotization':total}
									#Wallet_Customer.update_coins(values_wallet)
									_data = {'type_document':data['type_document'], 'pk_branch':branch.pk}
									#Resolution.add_number(_data)
									#serialized_employee = serializers.serialize('json', [employee])
									#employee = json.loads(serialized_employee)[0]['fields']
									serialized_cotization = serializers.serialize('json', [cotization])
									_cotization = json.loads(serialized_cotization)[0]
									#History_Invoice.create_history_invoice(cotization, employee, 'Created',branch)
									HistoryGeneral.create_history(
										action=HistoryGeneral.CREATED,
										class_models=HistoryGeneral.COTIZATION,
										class_models_json=_cotization,
										employee=employee.pk,
										username=employee.user_django.username,
										branch=employee.branch.pk
									)
								else:
									cotization.delete()
							result['message'] = "Cotizacion creada correctamente."
						else:
							# update invoice
							#print(data)
							cotization.type_document = data['type_document']
							cotization.number = data['number']
							cotization.prefix = data['prefix']
							cotization.branch = branch
							cotization.date = data['date']
							cotization.note = data['note']
							cotization.customer = customer
							cotization.hidden = True if data['type_document'] == 99 else False
							cotization.state = data['state']
							cotization.employee = employee
							cotization.invoice = Invoice.objects.filter(pk=data["invoice"]).first()
							cotization.remission = Remission.objects.filter(pk=data["remission"]).first()
							cotization.save()

							# buscamos los productos asociados y comparamos con los productos que vienen en la solicitud.
							# eliminar productos que ya no estan en uso y actualizar productos.
							for p in Details_Cotization.objects.filter(cotization=cotization):
								state = False
								for p2 in data["details"]:
									if p2["pk_item"] != 0:
										if p2["pk_item"] == p.pk:
											# actualizar producto.
											p.quantity = p2["quantity"]
											p.cost = p2["cost"]
											p.price = p2["price"]
											p.save()

											state = True
											break
								if not state:
									p.delete()
							# crear productos.
							result["pk_invoice"] = cotization.pk
							state = True
							if state:
								for i in data['details']:
									if i["pk_item"] == 0:
										value = Details_Cotization.create_details(i, cotization)
										if not value['result']:
											state = False
											result['message'] = value['message']
											break
										else:
											state = value['result']
											result['message'] = value['message']
											total += float(value['total'])

							if state:
								value = Payment_Forms_Cotization.create_paymentform(data, cotization, employee)
								state = value['result']
								result['message'] = value['message']
								if state:
									cotization.total = float(data["totalValue"])
									cotization.save()
									values_wallet = {"pk_customer":customer.pk, 'amount_cotization':total}
									#Wallet_Customer.update_coins(values_wallet)
									_data = {'type_document':data['type_document'], 'pk_branch':branch.pk}
									#Resolution.add_number(_data)
									#serialized_employee = serializers.serialize('json', [employee])
									#employee = json.loads(serialized_employee)[0]['fields']
									serialized_cotization = serializers.serialize('json', [cotization])
									_cotization = json.loads(serialized_cotization)[0]
									#History_Invoice.create_history_invoice(cotization, employee, 'Update',branch)
									HistoryGeneral.create_history(
										action=HistoryGeneral.UPDATE,
										class_models=HistoryGeneral.COTIZATION,
										class_models_json=_cotization,
										employee=employee.pk,
										username=employee.user_django.username,
										branch=employee.branch.pk
									)
							
							result['message'] = "Cotizacion actualizado correctamente."
						
						try:
							_invoice_data = cls.get_cotization({
								"token": data["token"],
								"pk_invoice": cotization.pk
							})
							_name_file = "cotization"+cotization.branch.company.documentI+str(cotization.prefix)+str(cotization.number)+".xml"
							_file_name_save = "cotization"+cotization.branch.company.documentI+str(cotization.prefix)+str(cotization.number)
							_invoice_data["data"]["path_dir"] = "media/cotization/"
							Create_PDF_Invoice(_invoice_data["data"], "pdf_cotization", _file_name_save)
							cotization.status_file = "Success"
							cotization.pdf = settings.URL_FILE+"media/cotization/"+str(_name_file).replace("xml", "pdf")
							cotization.save()
						except Exception as epdf:
							cotization.status_file = str(epdf)
							cotization.save()

						result['code'] = 200
						result['status'] = "OK"
					else:
						result["message"] = license['message']
				else:
					result["message"] = validate['message']
		except Exception as e:
			result["message"] = str(e)
			print(e, 'Created Cotization')
		return result

	@classmethod
	def get_list_cotization_credit(cls, branch):
		return [
			{
				"pk_invoice" : i.pk,
				"number": i.number,
				"prefix": i.prefix,
				"date": i.date,
				"total": i.total,
				"pk_customer":i.customer.pk,	
				"name_customer":i.customer.name
			}
			for i in cls.objects.filter(branch = branch, cancelled = False).order_by('-date')
		]

	@classmethod
	def delete_cotization(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"pk_invoice": None
		}
		if Employee.check_by_token(token=data["token"]):
			_cotization = cls.objects.filter(pk = data['pk_invoice']).first()
			if _cotization:
				employee = Employee.search_by_token(data['token'])
				#History_Invoice.create_history_invoice(_cotization, employee, 'Delete',employee.branch)
				serialized_cotization = serializers.serialize('json', [_cotization])
				cotization = json.loads(serialized_cotization)[0]
				HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.COTIZATION,
					class_models_json=cotization,
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				_cotization.delete()
				result["code"] = 200
				result["status"] = "OK"
				result["message"] = "Success"
			else:
				result["message"] = "Cotizacion no encontrada"
		return result

class Details_Cotization(models.Model):
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	tax = models.FloatField()
	cost = models.FloatField()
	price = models.FloatField()
	ipo = models.FloatField()
	discount = models.FloatField()
	cotization = models.ForeignKey(Cotization, on_delete = models.CASCADE)
	product = models.ForeignKey(Product, on_delete = models.CASCADE, null=True, blank=True)
	tax_value = models.IntegerField(default = 0, null=True, blank = True)

	@classmethod
	def create_details(cls, data, cotization:Cotization):
		result = False
		message = None
		try:
			_product = Product.objects.get(pk = data['pk'], branch = cotization.branch)
			details_cotization = cls(
				code = data['code'],
				name = data['product'],
				quantity = data['quantity'],
				tax = data['tax'],
				cost = data["cost"],
				price = data['price'],
				ipo = data['ipo'],
				discount = data['discount'],
				cotization = cotization,
				product = _product,
				tax_value = _product.tax.tax_num
			)
			details_cotization.save()
			result = True
			message = "Success"
			if result:
				if cotization.type_document != 99:
					value = Product.discount_product(data['pk'], cotization.branch, int(data['quantity']), cotization.employee)
					if not value['result']:
						result = value['result']
						message = value['message']
						cotization.delete()
						return {'result':result, 'message':message,'total':data['totalValue']}
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message,'total':data['totalValue']}

class Payment_Forms_Cotization(models.Model):
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE)
	payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE)
	payment_due_date = models.CharField(max_length = 12)
	cotization = models.ForeignKey(Cotization, on_delete = models.CASCADE)

	@classmethod
	def create_paymentform(cls, data, cotization:Cotization, employee):
		result = False
		message = None
		try:
			payment_form = cls.objects.filter(cotization=cotization).first()
			if not payment_form:
				payment_form = cls(
					payment_form = Payment_Form.objects.get(pk = data['payment_form']['paymentform']),
					payment_method = Payment_Method.objects.get(pk = data['payment_form']['paymentmethod']),
					payment_due_date = data['payment_form']['due_date'],
					cotization = cotization
				)
				payment_form.save()
				if data['payment_form']['paymentform'] == 2:
					cotization.cancelled = False
					cotization.save()
					_data = {
						"pk_invoice": cotization.pk,
						"amount":0,
						"note":"There are no pass yet",
						"pk_employee": employee.pk
					}
					PassCotization.create_pass(_data)
					result = True
					message = "Success"
				else:
					employee = Employee.objects.get(pk = employee.pk)
					branch = employee.branch
					serialized_product = serializers.serialize('json', [employee])
					employee = json.loads(serialized_product)[0]['fields']
					value = History_Invoice.create_history_invoice(data, employee, 'Created', branch)
					result = value['result']
					message = value['message']
			else:
				payment_form.payment_form = Payment_Form.objects.get(pk = data['payment_form']['paymentform'])
				payment_form.payment_method = Payment_Method.objects.get(pk = data['payment_form']['paymentmethod'])
				payment_form.payment_due_date = data['payment_form']['due_date']
				payment_form.save()

				# if data['payment_form']['paymentform'] == 2:
				# 	invoice.cancelled = False
				# 	invoice.save()
				# 	_data = {
				# 		"pk_invoice": invoice.pk,
				# 		"amount":0,
				# 		"note":"There are no pass yet",
				# 		"pk_employee": employee.pk
				# 	}
				# 	Pass.create_pass(_data)
				# 	result = True
				# 	message = "Success"
				# else:
				employee = Employee.objects.get(pk = employee.pk)
				branch = employee.branch
				serialized_product = serializers.serialize('json', [employee])
				employee = json.loads(serialized_product)[0]['fields']
				value = History_Invoice.create_history_invoice(data, employee, 'Update', branch)
				result = value['result']
				message = value['message']

		except Exception as e:
			message = f"{e} - Error Payment Form"
		return {'result':result, 'message':message}

class PassCotization(models.Model):
	number_pass = models.IntegerField()
	cotization = models.ForeignKey(Cotization, on_delete = models.CASCADE)
	amount = models.FloatField()
	date = models.DateTimeField(auto_now_add = True)
	note = models.TextField()
	employee = models.JSONField(null = True, blank = True)


	@classmethod
	def create_pass(cls, data):
		try:
			number = len(cls.objects.all())
		except Exception as e:
			pass
		cotization = Cotization.objects.get(pk = data['pk_invoice'])
		result = False
		message = None
		employee = Employee.objects.get(pk = data['pk_employee'])
		branch = employee.branch
		try:
			_pass = cls.objects.get(cotization = cotization)
			if _pass.amount < cotization.total:
				if float(data['amount']) <= (cotization.total - _pass.amount) and float(data['amount']) > 0:
					_pass.amount += float(data['amount'])
					message = "Credit to the cotization was accepted"
					result = True
				else:
					message = "You cannot pay more than the total cotization"
		except cls.DoesNotExist as e:
			_pass = cls(
				number_pass = number if number > 0 else 1,
				cotization = cotization,
				amount = data['amount'],
				note = data['note']
			)
			message = f"Credit to the cotization {cotization.number} was created successfully"
			result = True
		_pass.save()
		if _pass.amount == cotization.total:
			cotization.cancelled = True
			cotization.save()
			message = "The cotization has already been canceled"

		serialized_cotization = serializers.serialize('json', [cotization])
		serialized_customer = serializers.serialize('json', [cotization.customer])

		customer = json.loads(serialized_customer)[0]['fields']
		cotization = json.loads(serialized_cotization)[0]['fields']

		employee = serializers.serialize('json', [employee])

		if result:
			History_Pass.create_history_pass(cotization, data['amount'], customer, data['note'], employee, branch)
		return {'result':True, 'message':message}

	@classmethod
	def cancel_all_invoices(cls, data):
		employee = Employee.objects.get(pk = data['pk_employee'])
		customer = Customer.objects.get(pk = data['pk_customer'])
		pk = customer.pk
		cotization = Cotization.objects.filter(branch= employee.branch, cancelled = False, customer = customer)
		total = 0
		result = False
		message = None
		amount = data['amount']
		branch = employee.branch
		for i in cotization:
			total += i.total

		if total == amount:
			for i in cotization:
				_pass = cls.objects.get(cotization = i)
				_pass.amount = i.total
				_pass.save()
				i.cancelled = True
				i.save()
				result = True
				message = "cotization paid"
		else:
			note = None
			for i in cotization:
				if amount >= i.total:
					_pass = cls.objects.get(cotization = i)
					_pass.amount = i.total
					amount -= i.total
					i.cancelled = True
					_pass.save()
					note = "Pago cotization"
					serialized_cotization = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.customer])
					customer = json.loads(serialized_customer)[0]['fields']
					_cotization = json.loads(serialized_cotization)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_cotization, data['amount'], customer, note , __employee,branch)
				else:
					_pass = cls.objects.get(cotization = i)
					_pass.amount += amount
					_pass.save()
					note = "Abona al cotization"
					serialized_cotization = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.customer])
					customer = json.loads(serialized_customer)[0]['fields']
					_cotization = json.loads(serialized_cotization)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_cotization, data['amount'], customer, note , __employee,branch)
					if not _pass.cotization.cancelled:
						amount -= _pass.amount
						if amount <= 0:
							break
				i.save()
				result = True
				message = "Cotization paid"
		values = {"pk_customer": pk, "amount": amount}
		Wallet_Customer.update_wallet_customer(data)
		return {'result':result, 'message':message,"returned_value":amount}

class OrderBuy(models.Model):
	type_document = models.IntegerField()
	number = models.IntegerField()
	prefix = models.CharField(max_length = 7)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	date = models.CharField(max_length = 12)
	time = models.TimeField(auto_now_add = True)
	total = models.FloatField(null = True, blank = True)
	note = models.TextField(null = True, blank = True)
	supplier = models.ForeignKey(Supplier, on_delete = models.CASCADE)
	cancelled = models.BooleanField(default = True)
	hidden = models.BooleanField(default = False)
	state = models.CharField(max_length = 70,null = True, blank = True)
	annulled = models.BooleanField(default = False)
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE, null = True, blank = True)

	def __str__(self):
		return f"{self.prefix} - {self.number} by {self.branch.name}"

	@classmethod
	def get_order_buy(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				_order_buy = cls.objects.get(pk = data['pk_invoice'])
				serialized_order_buy = serializers.serialize('json', [_order_buy])
				order_buy = json.loads(serialized_order_buy)[0]
				result["data"] = order_buy['fields']
				result["data"]['pk_invoice'] = data['pk_invoice']
				list_details = []
				for i in Details_OrderBuy.objects.filter(order_buy = _order_buy):
					serialized_product = serializers.serialize('json', [i])
					product = json.loads(serialized_product)[0]['fields']
					product['subtotals'] = (product['price'] + product['ipo']) * product['quantity']
					product["pk_item"] = i.pk
					product["pk"] = i.product.pk
					list_details.append(product)
				result["data"]['details'] = list_details
				serialized_paymentform = serializers.serialize('json', [Payment_Forms_OrderBuy.objects.get(order_buy = _order_buy)])
				result["data"]['payment_form'] = json.loads(serialized_paymentform)[0]['fields']
				result["data"]['company'] = json.loads(serializers.serialize('json', [_order_buy.branch.company]))[0]['fields']
				result["data"]['metod'] = "Crédito" if result["data"]['payment_form'] == 2 else "Efectivo"
				serialized_supplier = serializers.serialize('json', [Supplier.objects.get(pk = _order_buy.supplier.pk)])
				result["data"]['supplier'] = json.loads(serialized_supplier)[0]['fields']
				_branch = Branch.objects.get(pk = _order_buy.branch.pk)
				branch = serializers.serialize('json', [_branch])
				result["data"]['branch'] = json.loads(branch)[0]['fields']
				resolution = {}
				try:
					resolution = serializers.serialize('json', [Resolution.objects.get(branch= _branch, type_document_id = result["data"]['type_document'])])
					result["data"]['resolution'] = json.loads(resolution)[0]['fields']
				except Exception as err:
					result["data"]['resolution'] = {}
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"
		except Exception as err2:
			result['message'] = str(err2)
		#print(result)
		return result

	@classmethod
	def get_list_order_buy(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				result["data"] = [
					{
						"type_document":i.type_document,
						'pk_order': i.pk,
						'number': i.number,
						'prefix': i.prefix,
						'date': i.date,
						'name_supplier': i.supplier.name,
						'total': Product.format_price(i.total),
						"state":i.state,
						"cancelled":i.cancelled,
						"annulled":i.annulled
					}
					for i in cls.objects.filter(branch = branch, type_document = data['type_document']).order_by('-pk')
				]
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"

		except Exception as e:
			result['message'] = str(e)
		#print(result)
		return result

	@classmethod
	def create_order_buy(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"pk_invoice": None
		}
		total = 0
		try:
			if Employee.check_by_token(token=data["token"]):
				supplier = Supplier.objects.get(pk = data['pk_supplier'])
				employee = Employee.search_by_token(data['token'])
				branch = employee.branch
				validate = License.validate_date(branch)
				if validate['result']:
					license = License.discount_license(branch)
					if license['result']:
						# validate order_buy create or modified
						order_buy = cls.objects.filter(pk=data["pk"]).first()
						if not order_buy:
							# create order_buy
							order_buy = cls(
								type_document = data['type_document'],
								number = data['number'],
								prefix = data['prefix'],
								branch = branch,
								date = data['date'],
								note = data['note'],
								supplier = supplier,
								hidden = True if data['type_document'] == 99 else False,
								state = data['state'],
								employee = employee
							)
							order_buy.save()
							from company.models import Consecutive
							Consecutive.consecutive_increment("oc", branch)
							result["pk_order"] = order_buy.pk
							state = True
							result['message'] = "Success"
							result['code'] = 200
							result['status'] = "OK"
							if state:
								for i in data['details']:
									value = Details_OrderBuy.create_details(i, order_buy)
									if not value['result']:
										state = False
										result['message'] = value['message']
										break
									else:
										state = value['result']
										result['message'] = value['message']
										total += float(value['total'])

							if state:
								value = Payment_Forms_OrderBuy.create_paymentform(data, order_buy, employee)
								state = value['result']
								result['message'] = value['message']
								if state:
									order_buy.total = total
									order_buy.save()
									values_wallet = {"pk_supplier":supplier.pk, 'amount_order_buy':total}
									#Wallet_supplier.update_coins(values_wallet)
									_data = {'type_document':data['type_document'], 'pk_branch':branch.pk}
									#Resolution.add_number(_data)
									#serialized_employee = serializers.serialize('json', [employee])
									#employee = json.loads(serialized_employee)[0]['fields']
									serialized_order_buy = serializers.serialize('json', [order_buy])
									order_buy = json.loads(serialized_order_buy)[0]
									#History_Invoice.create_history_invoice(order_buy, employee, 'Created',branch)
									HistoryGeneral.create_history(
										action=HistoryGeneral.CREATED,
										class_models=HistoryGeneral.ORDER_BUY,
										class_models_json=order_buy,
										employee=employee.pk,
										username=employee.user_django.username,
										branch=employee.branch.pk
									)
								else:
									order_buy.delete()
							result['message'] = "Orden de compra creada correctamente."
							result['code'] = 200
							result['status'] = "OK"
						else:
							# update invoice
							#print(data)
							order_buy.type_document = data['type_document']
							order_buy.number = data['number']
							order_buy.prefix = data['prefix']
							order_buy.branch = branch
							order_buy.date = data['date']
							order_buy.note = data['note']
							order_buy.supplier = supplier
							order_buy.hidden = True if data['type_document'] == 99 else False
							order_buy.state = data['state']
							order_buy.employee = employee
							order_buy.save()

							# buscamos los productos asociados y comparamos con los productos que vienen en la solicitud.
							# eliminar productos que ya no estan en uso y actualizar productos.
							for p in Details_OrderBuy.objects.filter(order_buy=order_buy):
								state = False
								for p2 in data["details"]:
									if p2["pk_item"] != 0:
										if p2["pk_item"] == p.pk:
											# actualizar producto.
											p.quantity = p2["quantity"]
											p.cost = p2["cost"]
											p.price = p2["price"]
											p.save()

											state = True
											break
								if not state:
									p.delete()
							# crear productos.
							result["pk_order"] = order_buy.pk
							state = True
							if state:
								for i in data['details']:
									if i["pk_item"] == 0:
										value = Details_OrderBuy.create_details(i, order_buy)
										if not value['result']:
											state = False
											result['message'] = value['message']
											break
										else:
											state = value['result']
											result['message'] = value['message']
											total += float(value['total'])

							if state:
								value = Payment_Forms_OrderBuy.create_paymentform(data, order_buy, employee)
								state = value['result']
								result['message'] = value['message']
								if state:
									order_buy.total = float(data["totalValue"])
									order_buy.save()
									values_wallet = {"pk_supplier":supplier.pk, 'amount_order_buy':total}
									#Wallet_supplier.update_coins(values_wallet)
									_data = {'type_document':data['type_document'], 'pk_branch':branch.pk}
									#Resolution.add_number(_data)
									#serialized_employee = serializers.serialize('json', [employee])
									#employee = json.loads(serialized_employee)[0]['fields']
									serialized_order_buy = serializers.serialize('json', [order_buy])
									order_buy = json.loads(serialized_order_buy)[0]
									#History_Invoice.create_history_invoice(order_buy, employee, 'Update',branch)
									HistoryGeneral.create_history(
										action=HistoryGeneral.UPDATE,
										class_models=HistoryGeneral.ORDER_BUY,
										class_models_json=order_buy,
										employee=employee.pk,
										username=employee.user_django.username,
										branch=employee.branch.pk
									)
							
							result['message'] = "Orden de compra actualizado correctamente."
							result['code'] = 200
							result['status'] = "OK"
					else:
						result["message"] = license['message']
				else:
					result["message"] = validate['message']
		except Exception as e:
			result["message"] = str(e)
			print(e, 'Created OrderBuy')
		return result

	@classmethod
	def get_list_order_buy_credit(cls, branch):
		return [
			{
				"pk_invoice" : i.pk,
				"number": i.number,
				"prefix": i.prefix,
				"date": i.date,
				"total": i.total,
				"pk_supplier":i.supplier.pk,	
				"name_supplier":i.supplier.name
			}
			for i in cls.objects.filter(branch = branch, cancelled = False).order_by('-date')
		]

	@classmethod
	def delete_order_buy(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"pk_invoice": None
		}
		if Employee.check_by_token(token=data["token"]):
			_order_buy = cls.objects.filter(pk = data['pk_invoice']).first()
			if _order_buy:
				employee = Employee.search_by_token(data['token'])
				#History_Invoice.create_history_invoice(_order_buy, employee, 'Delete',employee.branch)
				serialized_order_buy = serializers.serialize('json', [_order_buy])
				order_buy = json.loads(serialized_order_buy)[0]
				HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.ORDER_BUY,
					class_models_json=order_buy,
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				_order_buy.delete()
				result["code"] = 200
				result["status"] = "OK"
				result["message"] = "Success"
			else:
				result["message"] = "Orden de compra no encontrada"
		return result

class Details_OrderBuy(models.Model):
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	tax = models.FloatField()
	cost = models.FloatField()
	price = models.FloatField()
	ipo = models.FloatField()
	discount = models.FloatField()
	order_buy = models.ForeignKey(OrderBuy, on_delete = models.CASCADE)
	product = models.ForeignKey(Product, on_delete = models.CASCADE, null=True, blank=True)
	tax_value = models.IntegerField(default = 0, null=True, blank = True)

	@classmethod
	def create_details(cls, data, order_buy:OrderBuy):
		result = False
		message = None
		try:
			_product = Product.objects.get(pk = data['pk'], branch = order_buy.branch)
			details_order_buy = cls(
				code = data['code'],
				name = data['product'],
				quantity = data['quantity'],
				tax = data['tax'],
				cost = data["cost"],
				price = data['price'],
				ipo = data['ipo'],
				discount = data['discount'],
				order_buy = order_buy,
				product = _product,
				tax_value = _product.tax.tax_num
			)
			details_order_buy.save()
			result = True
			message = "Success"
			if result:
				if order_buy.type_document != 99:
					value = Product.discount_product(data['pk'], order_buy.branch, int(data['quantity']), order_buy.employee)
					if not value['result']:
						result = value['result']
						message = value['message']
						order_buy.delete()
						return {'result':result, 'message':message,'total':data['totalValue']}
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message,'total':data['totalValue']}

class Payment_Forms_OrderBuy(models.Model):
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE)
	payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE)
	payment_due_date = models.CharField(max_length = 12)
	order_buy = models.ForeignKey(OrderBuy, on_delete = models.CASCADE)

	@classmethod
	def create_paymentform(cls, data, order_buy:OrderBuy, employee):
		result = False
		message = None
		try:
			payment_form = cls.objects.filter(order_buy=order_buy).first()
			if not payment_form:
				payment_form = cls(
					payment_form = Payment_Form.objects.get(pk = data['payment_form']['paymentform']),
					payment_method = Payment_Method.objects.get(pk = data['payment_form']['paymentmethod']),
					payment_due_date = data['payment_form']['due_date'],
					order_buy = order_buy
				)
				payment_form.save()
				if data['payment_form']['paymentform'] == 2:
					order_buy.cancelled = False
					order_buy.save()
					_data = {
						"pk_invoice": order_buy.pk,
						"amount":0,
						"note":"There are no pass yet",
						"pk_employee": employee.pk
					}
					#PassOrderBuy.create_pass(_data)
					result = True
					message = "Success"
				else:
					employee = Employee.objects.get(pk = employee.pk)
					branch = employee.branch
					serialized_product = serializers.serialize('json', [employee])
					employee = json.loads(serialized_product)[0]['fields']
					value = History_Invoice.create_history_invoice(data, employee, 'Created', branch)
					result = value['result']
					message = value['message']
			else:
				payment_form.payment_form = Payment_Form.objects.get(pk = data['payment_form']['paymentform'])
				payment_form.payment_method = Payment_Method.objects.get(pk = data['payment_form']['paymentmethod'])
				payment_form.payment_due_date = data['payment_form']['due_date']
				payment_form.save()

				# if data['payment_form']['paymentform'] == 2:
				# 	invoice.cancelled = False
				# 	invoice.save()
				# 	_data = {
				# 		"pk_invoice": invoice.pk,
				# 		"amount":0,
				# 		"note":"There are no pass yet",
				# 		"pk_employee": employee.pk
				# 	}
				# 	Pass.create_pass(_data)
				# 	result = True
				# 	message = "Success"
				# else:
				employee = Employee.objects.get(pk = employee.pk)
				branch = employee.branch
				serialized_product = serializers.serialize('json', [employee])
				employee = json.loads(serialized_product)[0]['fields']
				value = History_Invoice.create_history_invoice(data, employee, 'Update', branch)
				result = value['result']
				message = value['message']

		except Exception as e:
			message = f"{e} - Error Payment Form"
		return {'result':result, 'message':message}
	
class InvoiceProvider(models.Model):
	type_document = models.IntegerField()
	number = models.CharField(max_length = 20)
	prefix = models.CharField(max_length = 7)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	date = models.CharField(max_length = 12)
	date_venc = models.CharField(max_length = 12)
	time = models.TimeField(auto_now_add = True)
	total = models.FloatField(null = True, blank = True)
	paid = models.FloatField(null = True, blank = True)
	note = models.TextField(null = True, blank = True)
	supplier = models.ForeignKey(Supplier, on_delete = models.CASCADE)
	cancelled = models.BooleanField(default = True)
	hidden = models.BooleanField(default = False)
	state = models.CharField(max_length = 70,null = True, blank = True)
	annulled = models.BooleanField(default = False)
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE, null = True, blank = True)
	order_buy = models.ManyToManyField(OrderBuy, null = True, blank = True)

	def __str__(self):
		return f"{self.prefix} - {self.number} by {self.branch.name}"

	@classmethod
	def get_invoice_provider(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				_invoice_provider = cls.objects.get(pk = data['pk_invoice'])
				serialized_invoice_provider = serializers.serialize('json', [_invoice_provider])
				invoice_provider = json.loads(serialized_invoice_provider)[0]
				result["data"] = invoice_provider['fields']
				result["data"]["total"] = Product.format_price(_invoice_provider.total)
				result["data"]['pk_invoice'] = data['pk_invoice']
				list_details = []
				for i in Details_InvoiceProvider.objects.filter(invoice_provider = _invoice_provider):
					serialized_product = serializers.serialize('json', [i])
					product = json.loads(serialized_product)[0]['fields']
					product['subtotals'] = (product['price'] + product['ipo']) * product['quantity']
					product["price"] = Product.format_price(i.price)
					product["pk_item"] = i.pk
					product["pk"] = i.product.pk
					list_details.append(product)
				result["data"]['details'] = list_details
				serialized_paymentform = serializers.serialize('json', [Payment_Forms_InvoiceProvider.objects.get(invoice_provider = _invoice_provider)])
				result["data"]['payment_form'] = json.loads(serialized_paymentform)[0]['fields']
				result["data"]['company'] = json.loads(serializers.serialize('json', [_invoice_provider.branch.company]))[0]['fields']
				result["data"]['metod'] = "Crédito" if result["data"]['payment_form'] == 2 else "Efectivo"
				serialized_supplier = serializers.serialize('json', [Supplier.objects.get(pk = _invoice_provider.supplier.pk)])
				result["data"]['supplier'] = json.loads(serialized_supplier)[0]['fields']
				_branch = Branch.objects.get(pk = _invoice_provider.branch.pk)
				branch = serializers.serialize('json', [_branch])
				result["data"]['branch'] = json.loads(branch)[0]['fields']
				_bill_to_pay = BillToPayInvoiceProvider.objects.filter(invoice_provider=_invoice_provider).first()
				result["data"]['bill_to_pay'] = json.loads(serializers.serialize('json', [_bill_to_pay]))[0]['fields']
				result["data"]["bill_to_pay"]["amount"] = Product.format_price(_bill_to_pay.amount)
				result["data"]['bill_to_pay']["credit"] = Product.format_price(_invoice_provider.total - _bill_to_pay.amount)
				resolution = {}
				try:
					resolution = serializers.serialize('json', [Resolution.objects.get(branch= _branch, type_document_id = result["data"]['type_document'])])
					result["data"]['resolution'] = json.loads(resolution)[0]['fields']
				except Exception as err:
					result["data"]['resolution'] = {}
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"
		except Exception as err2:
			result['message'] = str(err2)
		#print(result)
		return result

	@classmethod
	def get_list_invoice_provider(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"data": []
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				for i in cls.objects.filter(branch = branch, type_document = data['type_document']).order_by('-pk'):
					bill_to_pay = BillToPayInvoiceProvider.objects.filter(invoice_provider=i).first()
					try:
						print(i, bill_to_pay)
						result["data"].append(
							{
								"type_document":i.type_document,
								'pk_invoice_provider': i.pk,
								'paid': Product.format_price(bill_to_pay.amount) if bill_to_pay else None,
								'to_pay': Product.format_price(i.total - bill_to_pay.amount) if bill_to_pay else None,
								'number': i.number,
								'prefix': i.prefix,
								'date': i.date,
								'name_supplier': i.supplier.name,
								'pk_supplier': i.supplier.pk,
								'total': Product.format_price(i.total) if i.total else None,
								"state":i.state,
								"cancelled":i.cancelled,
								"annulled":i.annulled
							}
						)
					except Exception as e2:
						print(f"Error: {i.pk} "+str(e2))
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"

		except Exception as e:
			result['message'] = str(e)
		return result

	@classmethod
	def create_invoice_provider(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"pk_invoice": None
		}
		total = 0
		try:
			if Employee.check_by_token(token=data["token"]):
				supplier = Supplier.objects.get(pk = data['pk_supplier'])
				employee = Employee.search_by_token(data['token'])
				branch = employee.branch
				validate = License.validate_date(branch)
				if validate['result']:
					license = License.discount_license(branch)
					if license['result']:
						print(data)
						# validate invoice_provider create or modified
						invoice_provider = cls.objects.filter(pk=data["pk"]).first()
						if not invoice_provider:
							# create invoice_provider
							invoice_provider = cls.objects.create(
								type_document = data['type_document'],
								number = data['number'],
								prefix = data['prefix'],
								branch = branch,
								date = data['date'],
								note = data['note'],
								supplier = supplier,
								hidden = True if data['type_document'] == 99 else False,
								state = data['state'],
								employee = employee,
							)
							for ob in data["order_buy"]:
								invoice_provider.order_buy.add(OrderBuy.objects.filter(pk = ob).first())

							invoice_provider.save()
							result["pk_invoice"] = invoice_provider.pk
							state = True
							result['message'] = "Success"
							result['code'] = 200
							result['status'] = "OK"
							if state:
								for i in data['details']:
									value = Details_InvoiceProvider.create_details(i, invoice_provider)
									if not value['result']:
										state = False
										result['message'] = value['message']
										break
									else:
										state = value['result']
										result['message'] = value['message']
										total += float(value['total'])
							
							print(result)

							if state:
								value = Payment_Forms_InvoiceProvider.create_paymentform(data, invoice_provider, employee)
								state = value['result']
								result['message'] = value['message']
								if state:
									invoice_provider.total = total
									invoice_provider.save()

									BillToPayInvoiceProvider.create_bill_to_pay(
										{
											"amount": 0, 
											"number": 1, 
											"nota": "Cuenta por pagar a proveedores"
										},
										invoice_provider
									)
									
									serialized_invoice_provider = serializers.serialize('json', [invoice_provider])
									invoice_provider = json.loads(serialized_invoice_provider)[0]
									HistoryGeneral.create_history(
										action=HistoryGeneral.CREATED,
										class_models=HistoryGeneral.INVOICE_PROVIDER,
										class_models_json=invoice_provider,
										employee=employee.pk,
										username=employee.user_django.username,
										branch=employee.branch.pk
									)
								else:
									invoice_provider.delete()
							result['message'] = "Factura de proveedor correctamente."
							result['code'] = 200
							result['status'] = "OK"
						else:
							# update invoice
							#print(data)
							invoice_provider.type_document = data['type_document']
							invoice_provider.number = data['number']
							invoice_provider.prefix = data['prefix']
							invoice_provider.branch = branch
							invoice_provider.date = data['date']
							invoice_provider.note = data['note']
							invoice_provider.supplier = supplier
							invoice_provider.hidden = True if data['type_document'] == 99 else False
							invoice_provider.state = data['state']
							invoice_provider.employee = employee
							# remover items de order_buy y volver agregar.
							for ob2 in invoice_provider.order_buy.all():
								invoice_provider.order_buy.remove(ob2)

							for ob in data["order_buy"]:
								invoice_provider.order_buy.add(OrderBuy.objects.filter(pk = ob).first())
							invoice_provider.save()

							# buscamos los productos asociados y comparamos con los productos que vienen en la solicitud.
							# eliminar productos que ya no estan en uso y actualizar productos.
							for p in Details_InvoiceProvider.objects.filter(invoice_provider=invoice_provider):
								state = False
								for p2 in data["details"]:
									if p2["pk_item"] != 0:
										if p2["pk_item"] == p.pk:
											# actualizar producto.
											p.quantity = p2["quantity"]
											p.cost = p2["cost"]
											p.price = p2["price"]
											p.save()

											state = True
											break
								if not state:
									p.delete()
							# crear productos.
							result["pk_invoice"] = invoice_provider.pk
							state = True
							if state:
								for i in data['details']:
									if i["pk_item"] == 0:
										value = Details_InvoiceProvider.create_details(i, invoice_provider)
										if not value['result']:
											state = False
											result['message'] = value['message']
											break
										else:
											state = value['result']
											result['message'] = value['message']
											total += float(value['total'])

							if state:
								value = Payment_Forms_InvoiceProvider.create_paymentform(data, invoice_provider, employee)
								state = value['result']
								result['message'] = value['message']
								if state:
									invoice_provider.total = float(data["totalValue"])
									invoice_provider.save()

									serialized_invoice_provider = serializers.serialize('json', [invoice_provider])
									invoice_provider = json.loads(serialized_invoice_provider)[0]
									HistoryGeneral.create_history(
										action=HistoryGeneral.UPDATE,
										class_models=HistoryGeneral.INVOICE_PROVIDER,
										class_models_json=invoice_provider,
										employee=employee.pk,
										username=employee.user_django.username,
										branch=employee.branch.pk
									)
							
							result['message'] = "Factura de proveedor actualizado correctamente."
							result['code'] = 200
							result['status'] = "OK"
					else:
						result["message"] = license['message']
				else:
					result["message"] = validate['message']
		except Exception as e:
			result["message"] = str(e)
			print(e, 'Created invoice_provider')
		return result

	@classmethod
	def get_list_invoice_provider_credit(cls, branch):
		return [
			{
				"pk_invoice" : i.pk,
				"number": i.number,
				"prefix": i.prefix,
				"date": i.date,
				"total": i.total,
				"pk_supplier":i.supplier.pk,	
				"name_supplier":i.supplier.name
			}
			for i in cls.objects.filter(branch = branch, cancelled = False).order_by('-date')
		]

	@classmethod
	def delete_invoice_provider(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"pk_invoice": None
		}
		if Employee.check_by_token(token=data["token"]):
			_invoice_provider = cls.objects.filter(pk = data['pk_invoice']).first()
			if _invoice_provider:
				employee = Employee.search_by_token(data['token'])
				#History_Invoice.create_history_invoice(_invoice_provider, employee, 'Delete',employee.branch)
				serialized_invoice_provider = serializers.serialize('json', [_invoice_provider])
				invoice_provider = json.loads(serialized_invoice_provider)[0]
				HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.INVOICE_PROVIDER,
					class_models_json=invoice_provider,
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				_invoice_provider.delete()
				result["code"] = 200
				result["status"] = "OK"
				result["message"] = "Success"
			else:
				result["message"] = "Factura de proveedor no encontrada"
		return result

class Details_InvoiceProvider(models.Model):
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	tax = models.FloatField()
	cost = models.FloatField()
	price = models.FloatField()
	ipo = models.FloatField()
	discount = models.FloatField()
	invoice_provider = models.ForeignKey(InvoiceProvider, on_delete = models.CASCADE)
	product = models.ForeignKey(Product, on_delete = models.CASCADE, null=True, blank=True)
	tax_value = models.IntegerField(default = 0, null=True, blank = True)

	@classmethod
	def create_details(cls, data, invoice_provider:InvoiceProvider):
		result = False
		message = None
		try:
			_product = Product.objects.get(pk = data['pk'], branch = invoice_provider.branch)
			details_invoice_provider = cls(
				code = data['code'],
				name = data['product'],
				quantity = data['quantity'],
				tax = data['tax'],
				cost = data["cost"],
				price = data['price'],
				ipo = data['ipo'],
				discount = data['discount'],
				invoice_provider = invoice_provider,
				product = _product,
				tax_value = _product.tax.tax_num
			)
			details_invoice_provider.save()
			result = True
			message = "Success"
			if result:
				if invoice_provider.type_document != 99:
					value = Product.discount_product(data['pk'], invoice_provider.branch, int(data['quantity']), invoice_provider.employee)
					if not value['result']:
						result = value['result']
						message = value['message']
						invoice_provider.delete()
						return {'result':result, 'message':message,'total':data['totalValue']}
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message,'total':data['totalValue']}

class Payment_Forms_InvoiceProvider(models.Model):
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE)
	payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE)
	payment_due_date = models.CharField(max_length = 12)
	invoice_provider = models.ForeignKey(InvoiceProvider, on_delete = models.CASCADE)

	@classmethod
	def create_paymentform(cls, data, invoice_provider:InvoiceProvider, employee):
		result = False
		message = None
		try:
			payment_form = cls.objects.filter(invoice_provider=invoice_provider).first()
			if not payment_form:
				payment_form = cls(
					payment_form = Payment_Form.objects.get(pk = data['payment_form']['paymentform']),
					payment_method = Payment_Method.objects.get(pk = data['payment_form']['paymentmethod']),
					payment_due_date = data['payment_form']['due_date'],
					invoice_provider = invoice_provider
				)
				payment_form.save()
				if data['payment_form']['paymentform'] == 2:
					invoice_provider.cancelled = False
					invoice_provider.save()
					_data = {
						"pk_invoice": invoice_provider.pk,
						"amount":0,
						"note":"There are no pass yet",
						"pk_employee": employee.pk
					}
					result = True
					message = "Success"
				else:
					employee = Employee.objects.get(pk = employee.pk)
					branch = employee.branch
					serialized_product = serializers.serialize('json', [employee])
					employee = json.loads(serialized_product)[0]['fields']
					value = History_Invoice.create_history_invoice(data, employee, 'Created', branch)
					result = value['result']
					message = value['message']
			else:
				payment_form.payment_form = Payment_Form.objects.get(pk = data['payment_form']['paymentform'])
				payment_form.payment_method = Payment_Method.objects.get(pk = data['payment_form']['paymentmethod'])
				payment_form.payment_due_date = data['payment_form']['due_date']
				payment_form.save()

				# if data['payment_form']['paymentform'] == 2:
				# 	invoice.cancelled = False
				# 	invoice.save()
				# 	_data = {
				# 		"pk_invoice": invoice.pk,
				# 		"amount":0,
				# 		"note":"There are no pass yet",
				# 		"pk_employee": employee.pk
				# 	}
				# 	Pass.create_pass(_data)
				# 	result = True
				# 	message = "Success"
				# else:
				employee = Employee.objects.get(pk = employee.pk)
				branch = employee.branch
				serialized_product = serializers.serialize('json', [employee])
				employee = json.loads(serialized_product)[0]['fields']
				value = History_Invoice.create_history_invoice(data, employee, 'Update', branch)
				result = value['result']
				message = value['message']

		except Exception as e:
			message = f"{e} - Error Payment Form"
		return {'result':result, 'message':message}

class BillToPayInvoiceProvider(models.Model):
	number = models.IntegerField()
	invoice_provider = models.ForeignKey(InvoiceProvider, on_delete = models.CASCADE)
	amount = models.FloatField()
	date = models.DateTimeField()
	note = models.TextField()
	employee = models.JSONField(null = True, blank = True)

	@classmethod
	def create_bill_to_pay(cls, data, invoice_provider:InvoiceProvider):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
		}
		employee = invoice_provider.employee
		branch = employee.branch
		_bill_to_pay = cls.objects.filter(invoice_provider = invoice_provider).first()
		if _bill_to_pay:
			if _bill_to_pay.amount < invoice_provider.total:
				if float(data['amount']) <= (invoice_provider.total - _bill_to_pay.amount) and float(data['amount']) > 0:
					_bill_to_pay.amount += float(data['amount'])
					result["code"] = 200
					result["status"] = "OK"
					result["message"] = "Credit to the invoice provider was accepted"
					serialized_bill_to_pay = serializers.serialize('json', [_bill_to_pay])
					bill_to_pay = json.loads(serialized_bill_to_pay)[0]['fields']
					HistoryGeneral.create_history(
						action=HistoryGeneral.UPDATE,
						class_models=HistoryGeneral.Bill_TO_PAY,
						class_models_json=bill_to_pay,
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
				else:
					result["message"] = "You cannot pay more than the total invoice provider"
		else:
			_bill_to_pay = cls.objects.create(
				number = data["number"],
				invoice_provider = invoice_provider,
				amount = data['amount'],
				date = str(datetime.now()),
				note = data["nota"]
			)
			result["code"] = 200
			result["status"] = "OK"
			result["message"] = f"Credit to the invoice_provider {invoice_provider.number} was created successfully"
			bill_to_pay = cls.objects.filter(invoice_provider=invoice_provider).first()
			serialized_bill_to_pay = serializers.serialize('json', [bill_to_pay])
			bill_to_pay = json.loads(serialized_bill_to_pay)[0]['fields']
			HistoryGeneral.create_history(
				action=HistoryGeneral.CREATED,
				class_models=HistoryGeneral.Bill_TO_PAY,
				class_models_json=bill_to_pay,
				employee=employee.pk,
				username=employee.user_django.username,
				branch=employee.branch.pk
			)

		_bill_to_pay.save()
		if _bill_to_pay.amount == invoice_provider.total:
			invoice_provider.cancelled = True
			invoice_provider.save()
			result["message"] = "The invoice provider has already been canceled"

		return result

class PaymentInvoiceProvider(models.Model):
	number = models.IntegerField()
	invoice_provider = models.ForeignKey(InvoiceProvider, on_delete = models.CASCADE, null = True, blank = True)
	supplier = models.ForeignKey(Supplier, on_delete = models.CASCADE)
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE, null=True, blank=True)
	bank = models.ForeignKey(Bank, on_delete = models.CASCADE, null=True, blank=True)
	amount = models.FloatField()
	date = models.DateField(null=True, blank=True)
	note = models.TextField()
	employee = models.JSONField(null = True, blank = True)
	conciliation = models.BooleanField(default=False)

	@classmethod
	def create_payment(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"pk": None
		}
		if Employee.check_by_token(token=data["token"]):
			supplier = Supplier.objects.filter(pk = int(data['pk_supplier'])).first()
			employee = Employee.search_by_token(data['token'])
			branch = employee.branch
			invoice_provider = InvoiceProvider.objects.filter(pk = data["pkInvoiceProvider"]).first()
			_payment_invoice = cls.objects.filter(pk = int(data["pk"])).first()
			_payment_form = Payment_Form.objects.filter(pk = data["payment_form"]).first()
			bank = Bank.objects.filter(pk = data["bank"]).first()
			if not _payment_invoice:
				_payment_invoice = cls.objects.create(
					number = data["number"],
					invoice_provider = invoice_provider,
					supplier = supplier,
					payment_form = _payment_form,
					bank = bank,
					amount = float(data['totalValue']),
					date = data["date"],
					note = data["notas"]
				)
				from company.models import Consecutive
				Consecutive.consecutive_increment("ne", branch)
				result["code"] = 200
				result["status"] = "OK"
				result["message"] = "Success"
				
				BillToPayInvoiceProvider.create_bill_to_pay(
					{
						"amount": float(data['totalValue']),
					},
					invoice_provider
				)
				_payment_invoice = cls.objects.filter(invoice_provider=invoice_provider).first()
				result["pk"] = _payment_invoice.pk
				serialized_payment_invoice = serializers.serialize('json', [_payment_invoice])
				payment_invoice = json.loads(serialized_payment_invoice)[0]['fields']
				HistoryGeneral.create_history(
					action=HistoryGeneral.CREATED,
					class_models=HistoryGeneral.PAYMENT_INVOICE,
					class_models_json=payment_invoice,
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
			else:
				_payment_invoice.invoice_provider = invoice_provider
				_payment_invoice.supplier = supplier
				_payment_invoice.payment_form = _payment_form
				_payment_invoice.bank = bank
				_payment_invoice.amount = float(data['totalValue'])
				_payment_invoice.date = data["date"]
				_payment_invoice.note = data["notas"]
				_payment_invoice.save()
				result["pk"] = _payment_invoice.pk
				result["code"] = 200
				result["status"] = "OK"
				result["message"] = "Success"
				BillToPayInvoiceProvider.create_bill_to_pay(
					{
						"amount": float(data['totalValue']),
					},
					invoice_provider
				)

				serialized_payment_invoice = serializers.serialize('json', [cls.objects.filter(pk = int(data["pk"])).first()])
				payment_invoice = json.loads(serialized_payment_invoice)[0]['fields']
				HistoryGeneral.create_history(
					action=HistoryGeneral.UPDATE,
					class_models=HistoryGeneral.PAYMENT_INVOICE,
					class_models_json=payment_invoice,
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)

		return result
	
	@classmethod
	def get_list_payment(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"data": []
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				for a in InvoiceProvider.objects.filter(branch = branch).order_by('-pk'):
					for i in cls.objects.filter(invoice_provider=a).order_by("-pk"):
						bill_to_pay = BillToPayInvoiceProvider.objects.filter(invoice_provider=i.invoice_provider).first()
						result["data"].append(
							{
								"type_document":i.invoice_provider.type_document,
								'pk_invoice_provider': i.invoice_provider.pk,
								'paid': Product.format_price(bill_to_pay.amount) if bill_to_pay else None,
								'to_pay': Product.format_price(i.invoice_provider.total - bill_to_pay.amount) if bill_to_pay else None,
								'cuenta': bill_to_pay.note,
								'number_invoice': i.invoice_provider.number,
								'number': i.number,
								'date': i.date,
								'name_supplier': i.invoice_provider.supplier.name,
								'pk_supplier': i.invoice_provider.supplier.pk,
								'total': Product.format_price(i.invoice_provider.total),
								"state":i.invoice_provider.state,
								"cancelled":i.invoice_provider.cancelled,
								"annulled":i.invoice_provider.annulled,
								"pk": i.pk,
								"note": i.note,
								"conciliation": i.conciliation
							}
						)
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"

		except Exception as e:
			result['message'] = str(e)
		#print(result)
		return result
	
	@classmethod
	def get_payment(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
			"data": {}
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				payment_invoice_provider = cls.objects.filter(pk = data["pk"]).first()
				bill_to_pay = BillToPayInvoiceProvider.objects.filter(invoice_provider=payment_invoice_provider.invoice_provider).first()
				result["data"] = {
					"pk": payment_invoice_provider.pk,
					"type_document":payment_invoice_provider.invoice_provider.type_document,
					'pk_invoice_provider': payment_invoice_provider.invoice_provider.pk,
					'paid': bill_to_pay.amount if bill_to_pay else None,
					'to_pay': payment_invoice_provider.invoice_provider.total - bill_to_pay.amount if bill_to_pay else None,
					'number_invoice': payment_invoice_provider.invoice_provider.number,
					'number': payment_invoice_provider.number,
					'date': payment_invoice_provider.date,
					'name_supplier': payment_invoice_provider.supplier.name,
					'pk_supplier': payment_invoice_provider.supplier.pk,
					'total': payment_invoice_provider.invoice_provider.total,
					"state":payment_invoice_provider.invoice_provider.state,
					"cancelled":payment_invoice_provider.invoice_provider.cancelled,
					"annulled":payment_invoice_provider.invoice_provider.annulled,
					"payment_form": payment_invoice_provider.payment_form.pk,
					"bank": payment_invoice_provider.bank.pk,
					"note": payment_invoice_provider.note,
					"documentI": payment_invoice_provider.supplier.documentI,
					'total_paid': payment_invoice_provider.amount,
					"conciliation": payment_invoice_provider.conciliation
				}
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"

		except Exception as e:
			result['message'] = str(e)
		#print(result)
		return result
	
	@classmethod
	def delete_payment(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
		}
		if Employee.check_by_token(token=data["token"]):
			_payment_invoice_provider = cls.objects.filter(pk = data['pk']).first()
			if _payment_invoice_provider:
				employee = Employee.search_by_token(data['token'])
				#History_Invoice.create_history_invoice(_invoice_provider, employee, 'Delete',employee.branch)
				serialized_payment_invoice_provider = serializers.serialize('json', [_payment_invoice_provider])
				payment_invoice_provider = json.loads(serialized_payment_invoice_provider)[0]
				HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.PAYMENT_INVOICE,
					class_models_json=payment_invoice_provider,
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				_payment_invoice_provider.delete()
				result["code"] = 200
				result["status"] = "OK"
				result["message"] = "Success"
			else:
				result["message"] = "Pago no encontrada"
		return result
	
class History_Invoice(models.Model):
	ACTION_CHOICES = (
	    ('Created', 'Created'),
	    ('Modified', 'Modified'),
	    ('Deleted', 'Deleted'),
	    ('Annulled', 'Annulled'),
	)
	action = models.CharField(max_length=10, choices=ACTION_CHOICES,null = True, blank = True)
	invoice = models.JSONField()
	employee = models.JSONField()
	date_registration = models.DateTimeField(auto_now_add = True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE,null = True, blank = True)

	@classmethod
	def create_history_invoice(cls, invoice, employee, action,branch):
		result = False
		message = None
		try:
			hi = cls(
				invoice = invoice,
				employee = employee,
				action = action,
				branch = branch
			)
			hi.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

	@classmethod
	def get_history(cls, data):
		result = {
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			employee = Employee.search_by_token(token=data["token"])
			for h in cls.objects.filter(branch = employee.branch):
				result['data'].append({
					"pk": h.pk,
					"action": h.action,
					"employee": h.employee,
					"invoice": h.invoice,
					"date": str(h.date_registration)
				})
			result['code'] = 200
			result['message'] = ""
			result["status"] = "OK"

		return result

class History_Pass(models.Model):
	invoice = models.JSONField(null = True, blank = True)
	amount = models.FloatField(null = True, blank = True)
	customer = models.JSONField(null = True, blank = True)
	employee = models.JSONField(null = True, blank = True)
	note = models.TextField(null = True, blank = True)
	date_registration = models.DateTimeField(auto_now_add = True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE,null = True, blank = True)

	@classmethod
	def create_history_pass(cls, invoice, amount, customer, note, employee, branch):
		result = False
		message = None
		try:
			hp = cls(
				invoice = invoice,
				amount = amount,
				customer = customer,
				note = note,
				employee = employee,
				branch = branch
			)
			hp.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

class Note_Credit_Product(models.Model):
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	tax = models.FloatField()
	cost = models.FloatField()
	price = models.FloatField()
	ipo = models.FloatField()
	discount = models.FloatField()
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE)
	quantity_send = models.IntegerField(default = 0, null = True, blank = True)

	@classmethod
	def create_nc_by_product(cls, product, quantity, total, invoice):
		result = False
		message = None
		quantity_send = 0
		try:
			ncp = cls.objects.get(invoice = invoice)
		except Exception as e:
			ncp = None
		if ncp is None:
			try:
				ncp = cls(
					code = product.code,
					name = product.name,
					quantity = quantity,
					tax = product.tax,
					cost = product.cost,
					price = total,
					ipo = product.ipo,
					discount = product.discount,
					invoice = invoice,
					employee = invoice.employee,
				)
				ncp.save()
				ncp.quantity_send += quantity
				ncp.save()
				quantity_send = ncp.quantity_send
				ncp.price = round((ncp.cost + ncp.tax) * ncp.quantity_send)
				ncp.save()
				result = True
				message = "Success"
			except Exception as e:
				message = f'{e} Product NC'
		else:
			ncp.quantity_send += quantity
			ncp.save()
			ncp.price = round((ncp.cost + ncp.tax) * ncp.quantity_send)
			ncp.save()
			quantity_send = ncp.quantity_send
			result = True
			message = "Success"
		return {'result':result, 'message':message,'quantity_send':quantity_send}

























