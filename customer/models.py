from setting.models import *
from django.db import models
from company.models import Branch
from user.models import Employee
from django.core import serializers
import json

class Customer(models.Model):
	identification_number = models.TextField()
	dv = models.IntegerField(default = 0)
	name = models.CharField(max_length = 100)
	phone = models.CharField(max_length = 12,null=True, blank=True)
	phone_2 = models.CharField(max_length = 12,null=True, blank=True)
	address = models.CharField(max_length = 512,null=True, blank=True)
	email = models.EmailField(null=True, blank=True)
	email_optional = models.EmailField(null=True, blank=True)
	type_document_i = models.ForeignKey(Type_Document_I, on_delete = models.CASCADE, null=True, blank=True)
	type_organization = models.ForeignKey(Type_Organization, on_delete = models.CASCADE, null=True, blank=True)
	municipality = models.ForeignKey(Municipalities, on_delete = models.CASCADE)
	type_regime = models.ForeignKey(Type_Regimen, on_delete = models.CASCADE)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)

	def __str__(self):
		return f"{self.name} - {self.branch.name}"


	@staticmethod
	def dv_client(rut):
		factores = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
		rut_ajustado=str(rut).rjust( 15, '0')
		s = sum(int(rut_ajustado[14-i]) * factores[i] for i in range(14)) % 11
		if s > 1:
			return 11 - s
		else:
			return s

	@classmethod
	def delete_client(cls, data):
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			try:
				employee = Employee.search_by_token(token=data["token"])
				_customer = cls.objects.get(pk = data['pk_customer'])

				HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.CUSTOMER,
					class_models_json=cls.serializers_data(_customer),
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				_customer.delete()
				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"
			except cls.DoesNotExist as e:
				result['message'] = str(e)
		return result

	@classmethod
	def create_customer(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(token=data["token"])
				branch = employee.branch
				customer = cls.objects.filter(pk = data['pk_customer'] if data["pk_customer"] != "" else 0, branch = branch).first()
				if not customer:
					customer = cls(
						identification_number = data['identification_number'],
						dv = 0,#cls.dv_client(data['identification_number']),
						name = data['name'],
						phone = data['phone'] if data['phone'] else None,
						address = data['address'] if data['address'] else None,
						email = data['email'] if data['email'] else None,
						type_document_i = Type_Document_I.objects.filter(pk = data['type_document_identification_id']).first(),
						type_organization = Type_Organization.objects.filter(pk = data['type_organization_id']).first(),
						municipality = Municipalities.objects.filter(pk = data['municipality_id']).first(),
						type_regime = Type_Regimen.objects.filter(pk = data['type_regime_id']).first(),
						branch = branch
					)
					customer.save()
					if data['associate_person']:
						Associate_Person.create_associate_person(data['associate_person'], customer)
					if data['commercial_information']:
						Commercial_Information.create_commercial_information(data['commercial_information'], customer)

					HistoryGeneral.create_history(
						action=HistoryGeneral.CREATED,
						class_models=HistoryGeneral.CUSTOMER,
						class_models_json=cls.serializers_data(customer),
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
				else:
					customer.identification_number = data['identification_number']
					customer.dv = 0
					customer.name = data['name']
					customer.phone = data['phone'] if data['phone'] else None
					customer.address = data['address'] if data['address'] else None
					customer.email = data['email'] if data['email'] else None
					customer.municipality = Municipalities.objects.filter(pk = data['municipality_id']).first()
					customer.type_regime = Type_Regimen.objects.filter(pk = data['type_regime_id']).first()
					customer.save()
					#if data['associate_person']:
					Associate_Person.create_associate_person(data['associate_person'], customer)
					#if data['commercial_information']:
					#print(data['commercial_information'])
					Commercial_Information.create_commercial_information(data['commercial_information'], customer)

					HistoryGeneral.create_history(
						action=HistoryGeneral.UPDATE,
						class_models=HistoryGeneral.CUSTOMER,
						class_models_json=cls.serializers_data(customer),
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)

				result['code'] = 200
				result['message'] = "Success"
				result['status'] = "OK"
		except Exception as e:
			result['message'] = str(e)

		#print(result)
		return result

	@classmethod
	def create_consumidor_final(cls, branch):
		customer = cls(
			identification_number = 12345678,
			dv = 0,
			name = "Consumidor Final",
			type_document_i = Type_Document_I.objects.get(pk = 1),
			type_organization = Type_Organization.objects.get(pk = 1),
			municipality = Municipalities.objects.get(pk = 1),
			type_regime = Type_Regimen.objects.get(pk = 1),
			branch = branch
		)
		customer.save()
		employee = Employee.objects.filter(branch=branch).first()
		HistoryGeneral.create_history(
			action=HistoryGeneral.CREATED,
			class_models=HistoryGeneral.CUSTOMER,
			class_models_json=cls.serializers_data(customer),
			employee=employee.pk,
			username=employee.user_django.username,
			branch=employee.branch.pk
		)

	@staticmethod
	def serializers_data(obj):
		serialized_customer = serializers.serialize('json', [obj])
		return json.loads(serialized_customer)[0]

	@classmethod
	def get_list_customer(cls, data):
		result = {
			"data": [],
			"code": 400,
			"status": "OK",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			try:
				branch = Employee.search_by_token(token=data["token"]).branch
				for i in cls.objects.filter(branch = branch):
					customer = cls.serializers_data(i)
					data = customer['fields']
					data['pk_customer'] = customer['pk']
					data['name_type_regime'] = Type_Regimen.objects.filter(id=customer["fields"]["type_regime"]).first().name if Type_Regimen.objects.filter(id=customer["fields"]["type_regime"]).first() else ""
					data["associate_person"] = Associate_Person.get_data(customer=i)
					data["commercial_information"] = Commercial_Information.get_data(customer=i)
					result['data'].append(data)
				result["message"] = "Success"
				result['code'] = 200
				result['status'] = "OK"
			except Exception as e:
				print(e)
				result["message"] = str(e)
		#print(result)
		return result


	@classmethod
	def get_customer(cls, data):
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			try:
				customer = cls.serializers_data(cls.objects.get(pk = data['pk_customer']))
				result["data"] = customer['fields']
				result["data"]['name_type_document_i'] = Type_Document_I.objects.filter(pk = result["data"]['type_document_i']).first().name if Type_Document_I.objects.filter(pk = result["data"]['type_document_i']).first() else ""
				result["data"]['name_type_organization'] = Type_Organization.objects.filter(pk = result["data"]['type_organization']).first().name  if Type_Organization.objects.filter(pk = result["data"]['type_organization']) else ""
				result["data"]['name_municipality'] = Municipalities.objects.filter(pk = result["data"]['municipality']).first().name if Municipalities.objects.filter(pk = result["data"]['municipality']) else ""
				result["data"]['name_type_regime'] = Type_Regimen.objects.filter(pk = result["data"]['type_regime']).first().name if Type_Regimen.objects.filter(pk = result["data"]['type_regime']) else ""
				result["data"]['pk_customer'] = customer['pk']
				result["data"]["associate_person"] = Associate_Person.get_data(customer=customer['pk'])
				result["data"]["commercial_information"] = Commercial_Information.get_data(customer=customer['pk'])
				result["message"] = "Success"
				result['code'] = 200
				result['status'] = "OK"
			except Exception as e:
				result["message"] = str(e)
		#print(result)
		return result		

class Associate_Person(models.Model):
	name = models.CharField(max_length = 50)
	last_name = models.CharField(max_length = 50)
	email = models.EmailField()
	phone_1 = models.CharField(max_length = 15)
	phone_2 = models.CharField(max_length = 15)
	customer = models.ForeignKey(Customer, on_delete = models.CASCADE)

	def __str__(self):
		return f'{self.name} {self.last_name} by {self.customer.name}'

	@classmethod
	def create_associate_person(cls, data, customer):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			for ap in cls.objects.filter(customer=customer):
				state = False
				for i in data:
					if int(i["id"]) == ap.pk:
						state = True
						break
				if not state:
					ap.delete()

			for i in data:
				try:
					associate_person = cls.objects.filter(pk=i["id"]).first()
					if not associate_person:
						associate_person = cls(
							name = i['name'],
							last_name = i['last_name'],
							email = i['email'],
							phone_1 = i['phone_1'],
							phone_2 = i['phone_2'],
							customer = customer
						)
						associate_person.save()
					else:
						associate_person.name = i['name']
						associate_person.last_name = i['last_name']
						associate_person.email = i['email']
						associate_person.phone_1 = i['phone_1']
						associate_person.phone_2 = i['phone_2']
						associate_person.customer = customer
						associate_person.save()
					
					result = {
						"code": 200,
						"status": "OK",
						"message": "Success"
					}
				except Exception as e:
					result['message'] = str(e)
					#break
		except Exception as ex:
			result['message'] = str(ex)

		return result

	@classmethod
	def get_data(cls, customer):
		associate_person = []
		for a_s in cls.objects.filter(customer=customer):
			associate_person.append({
				"pk": a_s.pk,
				"name": a_s.name,
				"last_name": a_s.last_name,
				"email": a_s.email,
				"phone1": a_s.phone_1,
				"phone2": a_s.phone_2
			})
		return associate_person

class Commercial_Information(models.Model):
	payment_deadline = models.CharField(max_length = 50)
	list_price = models.ForeignKey(List_Price, on_delete = models.CASCADE, related_name='customer_list_price', null=True, blank=True)
	seller_info = models.ForeignKey(SellerInfo, on_delete = models.CASCADE, related_name='customer_seller', null=True, blank=True)
	term_payment = models.ForeignKey(TermPayment, on_delete = models.CASCADE, related_name='customer_term_payment', null=True, blank=True)
	cfdi = models.ForeignKey(CFDI, on_delete = models.CASCADE, related_name='customer_cfdi')
	payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE, related_name='customer_payment_method')
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE, related_name='customer_payment_form')
	customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name='customer_cfdi')

	@classmethod
	def create_commercial_information(cls, data, customer):
		result = False
		message = None
		try:
			commercial_information = cls.objects.filter(pk=data["ci_pk"] if data["ci_pk"] != "" else 0).first()
			if not commercial_information:
				_term_payment = TermPayment.objects.filter(pk = data["pk_term_payment"]).first()
				cp = cls(
					payment_deadline = _term_payment.name if _term_payment else "",
					list_price = List_Price.objects.filter(pk = data["pk_list_price"]).first(),
					seller_info = SellerInfo.objects.filter(pk = data['pk_seller']).first(),
					term_payment = _term_payment,
					cfdi = CFDI.objects.get(pk = data['cfdi']),
					payment_method = Payment_Method.objects.get(pk = data['payment_method']),
					payment_form = Payment_Form.objects.get(pk = data['payment_form']),
					customer = customer
				)
				cp.save()
			else:
				_term_payment = TermPayment.objects.filter(pk = data["pk_term_payment"]).first()
				commercial_information.payment_deadline = _term_payment.name if _term_payment else ""
				commercial_information.list_price = List_Price.objects.filter(pk = data["pk_list_price"]).first()
				commercial_information.seller_info = SellerInfo.objects.filter(pk = data['pk_seller']).first()
				commercial_information.term_payment = _term_payment
				commercial_information.cfdi = CFDI.objects.get(pk = data['cfdi'])
				commercial_information.payment_method = Payment_Method.objects.get(pk = data['payment_method'])
				commercial_information.payment_form = Payment_Form.objects.get(pk = data['payment_form'])
				commercial_information.customer = customer
				commercial_information.save()

			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		print(message)
		return {'result':result, 'message':message}

	@classmethod
	def get_data(cls, customer):
		commercial_information = {}
		for ci in cls.objects.filter(customer=customer):
			commercial_information = {
				"pk": ci.pk,
				"payment_deadline": ci.payment_deadline,
				"list_price": ci.list_price.pk,
				"list_price_name": ci.list_price.name,
				"seller": ci.seller_info.pk,
				"seller_name": ci.seller_info.name,
				"term_payment": ci.term_payment.pk,
				"term_payment_name": ci.term_payment.name,
				"cfdi": ci.cfdi.pk,
				"cfdi_name": ci.cfdi.name,
				"payment_method": ci.payment_method.pk,
				"payment_method_name": ci.payment_method.name,
				"payment_form": ci.payment_form.pk,
				"payment_form_name": ci.payment_form.name
			}
		return commercial_information

class Wallet_Customer(models.Model):
	amount = models.IntegerField()
	customer = models.ForeignKey(Customer, on_delete = models.CASCADE)
	note = models.TextField()
	date_register = models.DateField(auto_now_add= True)
	employee = models.ForeignKey(Employee, on_delete = models.CASCADE)
	coin = models.IntegerField(default = 0, null=True, blank = True)

	@classmethod
	def update_wallet_customer(cls, data):
		result = False
		message = None
		try:
			wallet_c = cls.objects.get(customer=Customer.objects.get(pk = data['pk_customer']))
			wallet_c.amount += data['amount']
			wallet_c.save()
		except Exception as e:
			print(e)
		return {'result':result, 'message':message}

	@classmethod
	def update_coins(cls, data):
		result = False
		message = None
		wallet_c = None
		try:
			customer = Customer.objects.get(pk = data['pk_customer'])
			if data['amount_invoice'] >= customer.branch.amount_min:
				wallet_c = cls.objects.get(customer = customer)
				wallet_c.coin += int(data['amount_invoice'] / customer.branch.value_coin)
				wallet_c.save()
				result = True
				message = "Success"
		except Exception as e:
			print(e)
		return {'result':result, 'message':message,'coin_generate':wallet_c.coin if wallet_c is not None else None}


