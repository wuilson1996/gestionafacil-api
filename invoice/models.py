from django.db import models
from user.models import Employee
from company.models import Branch, License, Resolution
from inventory.models import Product
from customer.models import *
from django.core import serializers
from setting.models import *
from datetime import date, datetime, timedelta
import json, qrcode, env
from io import BytesIO
from django.core.files import File
from PIL import Image

class Invoice(models.Model):
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
	cufe = models.CharField(max_length = 100,null = True, blank = True)
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE, null = True, blank = True)

	def __str__(self):
		return f"{self.prefix} - {self.number} by {self.branch.name}"

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
	def get_invoice(cls, pk):
		_invoice = cls.objects.get(pk = pk)
		serialized_invoice = serializers.serialize('json', [_invoice])
		invoice = json.loads(serialized_invoice)[0]
		data = invoice['fields']
		data['pk_invoice'] = pk
		list_details = []
		for i in Details_Invoice.objects.filter(invoice = _invoice):
			serialized_invoice = serializers.serialize('json', [i])
			product = json.loads(serialized_invoice)[0]['fields']
			product['subtotals'] = (product['price'] + product['ipo']) * product['quantity']
			list_details.append(product)
		data['details'] = list_details
		serialized_paymentform = serializers.serialize('json', [Payment_Forms.objects.get(invoice = _invoice)])
		data['payment_form'] = json.loads(serialized_paymentform)[0]['fields']
		data['company'] = json.loads(serializers.serialize('json', [_invoice.branch.company]))[0]['fields']
		data['metod'] = "Crédito" if data['payment_form'] == 2 else "Efectivo"
		serialized_customer = serializers.serialize('json', [Customer.objects.get(pk = _invoice.customer.pk)])
		data['customer'] = json.loads(serialized_customer)[0]['fields']
		_branch = Branch.objects.get(pk = _invoice.branch.pk)
		branch = serializers.serialize('json', [_branch])
		data['branch'] = json.loads(branch)[0]['fields']
		resolution = serializers.serialize('json', [Resolution.objects.get(branch= _branch, type_document_id = data['type_document'])])
		data['resolution'] = json.loads(resolution)[0]['fields']

		return data

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
		branch = Employee.objects.get(pk = data['pk_employee']).branch
		result = False
		message = None
		_data = None
		try:
			_data = [
				{
					"type_document":i.type_document,
					'pk_invoice': i.pk,
					'number': i.number,
					'prefix': i.prefix,
					'date': i.date,
					'name_client': i.customer.name,
					'total': i.total,
					"state":i.state,
					"cancelled":i.cancelled,
					"annulled":i.annulled
				}
				for i in cls.objects.filter(branch = branch, type_document = data['type_document']).order_by('-pk')
			]
		except Exception as e:
			print(e)
			message = str(e)
			_data = []
		return _data

	@classmethod
	def create_invoice(cls, data):
		result = False
		message = None
		employee = Employee.objects.get(pk = data['pk_employee'])
		total = 0
		pk_invoice = None
		customer = Customer.objects.get(pk = data['pk_customer'])
		branch = employee.branch
		try:			
			validate = License.validate_date(employee.branch)
			if validate['result']:
				license = License.discount_license(employee.branch)
				if license['result']:
					invoice = cls(
						type_document = data['type_document'],
						number = data['number'],
						prefix = data['prefix'],
						branch = employee.branch,
						date = data['date'],
						note = data['note'],
						customer = customer,
						hidden = True if data['type_document'] == 99 else False,
						state = data['state'],
						employee = employee
					)
					invoice.save()
					pk_invoice = invoice.pk
					result = True
					message = "Success"
					if result:
						for i in data['details']:
							value = Details_Invoice.create_details(i, invoice)
							if not value['result']:
								result = False
								message = value['message']
								break
							else:
								result = value['result']
								message = value['message']
								total += float(value['total'])
					if result:
						value = Payment_Forms.create_paymentform(data, invoice, employee)
						result = value['result']
						message = value['message']
						if result:
							invoice.total = total
							invoice.save()
							values_wallet = {"pk_customer":customer.pk, 'amount_invoice':total}
							Wallet_Customer.update_coins(values_wallet)
							_data = {'type_document':data['type_document'], 'pk_branch':employee.branch.pk}
							Resolution.add_number(_data)
							serialized_employee = serializers.serialize('json', [employee])
							employee = json.loads(serialized_employee)[0]['fields']
							serialized_invoice = serializers.serialize('json', [invoice])
							invoice = json.loads(serialized_invoice)[0]['fields']
							History_Invoice.create_history_invoice(invoice, employee, 'Created',branch)
						else:
							invoice.delete()
				else:
					result = license['result']
					message = license['message']
			else:
				result = validate['result']
				message = validate['message']
		except Exception as e:
			message = str(e)
			print(e, 'Created Invoice')
		return {'result':result, 'message':message,'pk_invoice': pk_invoice}

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
	tax_value = models.IntegerField(default = 0, null=True, blank = True)

	@classmethod
	def create_details(cls, data, invoice):
		result = False
		message = None
		try:
			details_invoice = cls(
				code = data['code'],
				name = data['product'],
				quantity = data['quantity'],
				tax = data['tax'],
				cost = 0,
				price = data['price'],
				ipo = data['ipo'],
				discount = data['discount'],
				invoice = invoice,
				tax_value = Product.objects.get(code = data['code'], branch = invoice.branch).tax
			)
			details_invoice.save()
			result = True
			message = "Success"
			if result:
				if invoice.type_document != 99:
					value = Product.discount_product(data['code'], invoice.branch, int(data['quantity']), invoice.employee)
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
	payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE)
	payment_due_date = models.CharField(max_length = 12)
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)

	@classmethod
	def create_paymentform(cls, data, invoice, employee):
		result = False
		message = None
		try:
			payment_form = cls(
				payment_form = Payment_Form.objects.get(_id = data['payment_form']['paymentform']),
				payment_method = Payment_Method.objects.get(_id = data['payment_form']['paymentmethod']),
				payment_due_date = data['payment_form']['due_date'],
				invoice = invoice
			)
			payment_form.save()
			if data['payment_form']['paymentform'] == 2:
				invoice.cancelled = False
				invoice.save()
				_data = {
					"pk_invoice": invoice.pk,
					"amount":0,
					"note":"There are no pass yet",
					"pk_employee": employee.pk
				}
				Pass.create_pass(_data)
				result = True
				message = "Success"
			else:
				employee = Employee.objects.get(pk = employee.pk)
				serialized_product = serializers.serialize('json', [employee])
				employee = json.loads(serialized_product)[0]['fields']
				value = History_Invoice.create_history_invoice(data, employee, 'Created')
				result = value['result']
				message = value['message']
		except Exception as e:
			message = f"{e} - Error Payment Form"
		return {'result':result, 'message':message}

class Pass(models.Model):
	number_pass = models.IntegerField()
	invoice = models.ForeignKey(Invoice, on_delete = models.CASCADE)
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
		invoice = Invoice.objects.get(pk = data['pk_invoice'])
		result = False
		message = None
		employee = Employee.objects.get(pk = data['pk_employee'])
		branch = employee.branch
		try:
			_pass = cls.objects.get(invoice = invoice)
			if _pass.amount < invoice.total:
				if float(data['amount']) <= (invoice.total - _pass.amount) and float(data['amount']) > 0:
					_pass.amount += float(data['amount'])
					message = "Credit to the invoice was accepted"
					result = True
				else:
					message = "You cannot pay more than the total invoice"
		except cls.DoesNotExist as e:
			_pass = cls(
				number_pass = number if number > 0 else 1,
				invoice = invoice,
				amount = data['amount'],
				note = data['note']
			)
			message = f"Credit to the invoice {invoice.number} was created successfully"
			result = True
		_pass.save()
		if _pass.amount == invoice.total:
			invoice.cancelled = True
			invoice.save()
			message = "The invoice has already been canceled"

		serialized_invoice = serializers.serialize('json', [invoice])
		serialized_customer = serializers.serialize('json', [invoice.customer])

		customer = json.loads(serialized_customer)[0]['fields']
		invoice = json.loads(serialized_invoice)[0]['fields']

		employee = serializers.serialize('json', [employee])

		if result:
			History_Pass.create_history_pass(invoice, data['amount'], customer, data['note'], employee, branch)
		return {'result':True, 'message':message}

	@classmethod
	def cancel_all_invoices(cls, data):
		employee = Employee.objects.get(pk = data['pk_employee'])
		customer = Customer.objects.get(pk = data['pk_customer'])
		pk = customer.pk
		invoice = Invoice.objects.filter(branch= employee.branch, cancelled = False, customer = customer)
		total = 0
		result = False
		message = None
		amount = data['amount']
		branch = employee.branch
		for i in invoice:
			total += i.total

		if total == amount:
			for i in invoice:
				_pass = cls.objects.get(invoice = i)
				_pass.amount = i.total
				_pass.save()
				i.cancelled = True
				i.save()
				result = True
				message = "Invoice paid"
		else:
			note = None
			for i in invoice:
				if amount >= i.total:
					_pass = cls.objects.get(invoice = i)
					_pass.amount = i.total
					amount -= i.total
					i.cancelled = True
					_pass.save()
					note = "Pago factura"
					serialized_invoice = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.customer])
					customer = json.loads(serialized_customer)[0]['fields']
					_invoice = json.loads(serialized_invoice)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_invoice, data['amount'], customer, note , __employee,branch)
				else:
					_pass = cls.objects.get(invoice = i)
					_pass.amount += amount
					_pass.save()
					note = "Abona a la factura"
					serialized_invoice = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.customer])
					customer = json.loads(serialized_customer)[0]['fields']
					_invoice = json.loads(serialized_invoice)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_invoice, data['amount'], customer, note , __employee,branch)
					if not _pass.invoice.cancelled:
						amount -= _pass.amount
						if amount <= 0:
							break
				i.save()
				result = True
				message = "Invoice paid"
		values = {"pk_customer": pk, "amount": amount}
		Wallet_Customer.update_wallet_customer(data)
		return {'result':result, 'message':message,"returned_value":amount}

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

























