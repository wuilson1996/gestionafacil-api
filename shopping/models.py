from django.db import IntegrityError
from inventory.models import Product, Supplier
from setting.models import Payment_Form, Payment_Method
from django.core import serializers
from company.models import Branch, License
from user.models import Employee
from django.db import models
import json

class Shopping(models.Model):
	number = models.CharField(max_length = 50, unique = True)
	date = models.DateTimeField(auto_now_add = True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE) 
	date_registration = models.CharField(max_length = 10)
	cancelled = models.BooleanField(default = True)
	annulled = models.BooleanField(default = False)
	total = models.FloatField(null = True, blank = True)

	def __str__(self):
		return f"{self.number} by {self.branch.name} - {self.date}"

	@classmethod
	def verified_invoice(cls, data):
		result = False
		message = None
		try:
			cls.objects.get(number=data['number'], branch = Employee.objects.get(pk = data['pk_employee']).branch)
			result = True
			message = "Esta factura de compra ya existe."
		except cls.DoesNotExist as e:
			message = None
		return {'result':result, 'message':message}

	@staticmethod
	def serializers_obj(obj):
		return json.loads(serializers.serialize('json', [obj]))

	@classmethod
	def get_invoice_shopping(cls, data):
		result = False
		message = None
		_data = []
		try:
			shopping = cls.objects.filter(branch = data['pk_branch'])
			_data = [cls.serializers_obj(obj) for obj in shopping]
			result = True
			message = 'Success'
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message,'data':_data}

	@classmethod
	def create_shopping(cls, data):
		result = False
		message = None
		total = 0
		try:
			branch = Employee.objects.get(pk = data['pk_employee']).branch
			value = License.discount_license(branch)
			if value['result']:
				shopping = cls(
					number = data['number'],
					branch = branch,
					supplier = Supplier.objects.get(pk = data['pk_supplier']),
					date_registration = data['date_registration'],
				)
				shopping.save()
				result = True
				message = "Success"
				for i in data['details']:
					result = Details.create_details(i, shopping)
					total += result['total']
					if not result['result']:
						message = result['message']
						result = result['result']
						break
				result = PaymentFormShopping.create_payment_form(data, shopping)
				shopping.total = total
				shopping.save()
				if not result['result']:
					message = result['message']
					result = result['result']
				else:
					result = result['result']
			else:
				result = value['result']
				message = value['message']
		except IntegrityError as inte:
			message = "This invoice has already been registered."
		except Exception as e:
			message = f"{e} - Shopping Invoice"
		return {'result':result, 'message':message}


class Details(models.Model):
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	tax = models.IntegerField()
	cost = models.FloatField()
	price_1 = models.FloatField()
	price_2 = models.FloatField()
	price_3 = models.FloatField()
	ipo = models.FloatField()
	discount = models.FloatField()
	shopping = models.ForeignKey(Shopping, on_delete = models.CASCADE)

	def __str__(self):
		return f"{self.shopping.number} by {self.shopping.branch.name} - {self.shopping.date}"

	@classmethod
	def create_details(cls,data,shopping):
		result = False
		message = None
		total = 0
		try:
			details = cls(
				code= data['code'],
			    name= data['name'],
			    quantity= data['quantity'],
			    tax= data['tax'],
			    cost= data['cost'],
			    price_1= data['price_1'],
			    price_2= data['price_2'],
			    price_3= data['price_3'],
			    ipo= data['ipo'],
			    discount= data['discount'],
			    shopping= shopping
			)
			details.save()
			result = True
			message= "Success"
			if result:
				result = cls.update_product_by_shopping(data, shopping)
			total += int(data['price_1']) * int(data['quantity'])
			message = result['message']
			result = result['result']
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message,'total':total}


	@staticmethod
	def update_product_by_shopping(data, shopping):
		result = False
		message = None
		try:
			product = Product.objects.get(code = data['code'], branch=shopping.branch)
			product.tax = data['tax']
			product.quantity += int(data['quantity'])
			product.price_1 = data['price_1']
			product.price_2 = data['price_2']
			product.price_3 = data['price_3']
			product.ipo = data['ipo']
			product.discount = data['discount']
			product.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}


class PaymentFormShopping(models.Model):
	shopping = models.ForeignKey(Shopping, on_delete = models.CASCADE)
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE)
	payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE)
	payment_due_date = models.CharField(max_length = 10)

	def __str__(self):
		return f"{self.shopping.number} by {self.shopping.branch.name} - {self.shopping.date}"

	@classmethod
	def create_payment_form(cls, data, shopping):
		result = False
		message = None
		try:
			payment_form = cls(
				shopping = shopping,
				payment_form = Payment_Form.objects.get(_id = data['payment_form']['pk_paymentform']),
				payment_method = Payment_Method.objects.get(_id = data['payment_form']['pk_paymentmethod']),
				payment_due_date = data['payment_form']['payment_due_date']
			)
			payment_form.save()
			employee = Employee.objects.get(pk = data['pk_employee'])
			if int(data['payment_form']['pk_paymentform']) == 2:
				shopping.cancelled = False
				shopping.save()
				_data = {
					"pk_shopping": shopping.pk,
					"amount":0,
					"note":"There are no pass yet",
					"pk_employee": employee.pk
				}
				Pass.create_pass(_data)
				result = True
				message = "Success"
			else:
				serialized_product = serializers.serialize('json', [employee])
				employee = json.loads(serialized_product)[0]['fields']
				serialized_supplier = serializers.serialize('json', [shopping.supplier])
				supplier = json.loads(serialized_supplier)[0]['fields']
				serialized_shopping = serializers.serialize('json', [shopping])
				_shopping = json.loads(serialized_shopping)[0]['fields']
			value = History_Shopping.create_history(_shopping, supplier, employee)
			result = value['result']
			message = value['message']
		except Exception as e:
			message = str(e)+" employee not found"
		return {'result':result, 'message':message}

class Pass(models.Model):
	number_pass = models.IntegerField()
	shopping = models.ForeignKey(Shopping, on_delete = models.CASCADE)
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
		shopping = Shopping.objects.get(pk = data['pk_shopping'])
		result = False
		message = None
		try:
			_pass = cls.objects.get(shopping = shopping)
			if _pass.amount < shopping.total:
				if float(data['amount']) <= (shopping.total - _pass.amount) and float(data['amount']) > 0:
					_pass.amount += float(data['amount'])
					message = "Credit to the invoice was accepted"
					result = True
					_pass.save()
				else:
					message = "You cannot pay more than the total invoice"
		except cls.DoesNotExist as e:
			_pass = cls(
				number_pass = number if number > 0 else 1,
				shopping = shopping,
				amount = data['amount'],
				note = data['note']
			)
			message = f"Credit to the invoice {shopping.number} was created successfully"
			result = True
			_pass.save()
		if _pass.amount == shopping.total:
			shopping.cancelled = True
			shopping.save()
			message = "The invoice has already been canceled"

		serialized_invoice = serializers.serialize('json', [shopping])
		serialized_supplier = serializers.serialize('json', [shopping.supplier])
		employee = Employee.objects.get(pk = data['pk_employee'])
		serialized_product = serializers.serialize('json', [employee])
		employee = json.loads(serialized_product)[0]['fields']
		supplier = json.loads(serialized_supplier)[0]['fields']
		shopping = json.loads(serialized_invoice)[0]['fields']
		if result:
			History_Pass.create_history_pass(shopping,data['amount'], supplier,data['note'], employee, data['transaction'] if 'transaction' in data else None)
		return {'result':True, 'message':message}

	@classmethod
	def cancel_all_invoices(cls, data):
		employee = Employee.objects.get(pk = data['pk_employee'])
		supplier = Supplier.objects.get(pk = data['pk_supplier'])
		shopping = Shopping.objects.filter(branch= employee.branch, cancelled = False, supplier = supplier)
		total = 0
		result = False
		message = None
		amount = data['amount']
		for i in shopping:
			total += i.total
		if total == amount:
			for i in shopping:
				_pass = cls.objects.get(shopping = i)
				_pass.amount = i.total
				_pass.save()
				i.cancelled = True
				i.save()
				result = True
				message = "Invoice paid"
		else:
			note = None
			for i in shopping:
				if amount >= i.total:
					_pass = cls.objects.get(shopping = i)
					_pass.amount = i.total
					amount -= i.total
					i.cancelled = True
					_pass.save()
					note = "Pago factura"
					serialized_shopping = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.supplier])
					supplier = json.loads(serialized_customer)[0]['fields']
					_shopping = json.loads(serialized_shopping)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_shopping, data['amount'], supplier, note , __employee)
					result = True
					message = "Invoice paid"
				else:
					_pass = cls.objects.get(shopping = i)
					_pass.amount += amount
					_pass.save()
					note = "Abona a la factura"
					serialized_shopping = serializers.serialize('json', [i])
					serialized_customer = serializers.serialize('json', [i.supplier])
					supplier = json.loads(serialized_customer)[0]['fields']
					_shopping = json.loads(serialized_shopping)[0]['fields']
					_employee = serializers.serialize('json', [employee])
					__employee = json.loads(_employee)[0]['fields']
					History_Pass.create_history_pass(_shopping, data['amount'], supplier, note , __employee)
					result = True
					message = "Invoice paid"
					if not _pass.shopping.cancelled:
						amount -= _pass.amount
						if amount <= 0:
							break
				i.save()
		
		return {'result':result, 'message':message,"returned_value":amount}


class History_Shopping(models.Model):
	shopping = models.JSONField(null = True, blank = True)
	employee = models.JSONField(null = True, blank = True)
	supplier = models.JSONField(null = True, blank = True)
	date_registration = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return f"Number: {self.shopping['number']} - Proveedor: {self.supplier['name']} by {self.employee['user_name'].capitalize()} - {self.date_registration} "

	@classmethod
	def create_history(cls,shopping, supplier, employee):
		result = False
		message = None
		try:
			hs = cls(
				shopping = shopping,
				supplier = supplier,
				employee = employee
			)
			hs.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result': result, 'message':message}

class History_Pass(models.Model):
	shopping = models.JSONField(null = True, blank = True)
	amount = models.FloatField(null = True, blank = True)
	customer = models.JSONField(null = True, blank = True)
	employee = models.JSONField(null = True, blank = True)
	note = models.TextField(null = True, blank = True)
	number_transaction = models.CharField(max_length = 50,default = 0,null = True, blank = True)
	date_registration = models.DateTimeField(auto_now_add = True)

	@classmethod
	def create_history_pass(cls, shopping, amount, customer, note, employee, trasaction = None):
		result = False
		message = None
		try:
			hp = cls(
				shopping = shopping,
				amount = amount,
				customer = customer,
				note = note,
				employee = employee,
				number_transaction = trasaction if trasaction is not None else None
			)
			hp.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}