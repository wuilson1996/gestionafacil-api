import json, requests, env, convert_base64_to_png as convert, base64
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from django.db import IntegrityError
from django.core import serializers
from django.db import models
from setting.models import *
from io import BytesIO
from PIL import Image
from rest_framework.authtoken.models import Token


class Company(models.Model):
	type_document_identification = models.ForeignKey(Type_Document_I, on_delete = models.CASCADE, null = True, blank = True)
	type_organization = models.ForeignKey(Type_Organization, on_delete = models.CASCADE, null = True, blank = True)
	type_regime = models.ForeignKey(Type_Regimen, on_delete = models.CASCADE, null = True, blank = True)
	municipality = models.ForeignKey(Municipalities, on_delete = models.CASCADE, null = True, blank = True)
	sector = models.ForeignKey(Sector, on_delete = models.CASCADE, null = True, blank = True)
	documentI = models.CharField(max_length=100, null=True, blank=True)
	name = models.CharField(max_length=200)
	name_commercial = models.CharField(max_length=200)
	address = models.CharField(max_length = 150)
	phone = models.CharField(max_length = 15)
	email = models.EmailField()
	verified = models.BooleanField(default= False)
	production = models.BooleanField(default = False)
	token = models.CharField(max_length = 100, null = True, blank = True)
	logo = models.ImageField(upload_to = "Logo_Company", null = True, blank = True,default = "Logo_Company/withOut.png")
	logo_b64 = models.TextField(null = True, blank = True)
	software_company = models.CharField(max_length = 150, null = True, blank = True)
	testsetid = models.CharField(max_length = 150, null = True, blank = True)
	ping = models.IntegerField(null = True, blank=True)
	site = models.CharField(max_length = 512, null = True, blank = True)
	cant_employee = models.CharField(max_length = 150, null = True, blank = True)
	money = models.CharField(max_length = 50, null = True, blank = True)
	decimal = models.CharField(max_length = 50, null = True, blank = True)
	point = models.CharField(max_length = 50, null = True, blank = True)
	cer_file = models.FileField(upload_to="cert", null=True, blank=True)
	key_file = models.FileField(upload_to="cert", null=True, blank=True)
	pwd = models.CharField(max_length=200, null=True, blank=True)
	#type_current = models.CharField(max_length = 3,null = True, blank=True) #COP

	def __str__(self):
		return self.name

	@staticmethod
	def dv(rut):
		factores = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
		rut_ajustado=str(rut).rjust( 15, '0')
		s = sum(int(rut_ajustado[14-i]) * factores[i] for i in range(14)) % 11
		if s > 1:
			return 11 - s
		else:
			return s

	@staticmethod
	def create_company_api(cls,data):
		_url = Operation.objects.get(pk = 1).url_api
		url = f"{_url}/api/ubl2.1/config/{data['documentI']}/{cls.dv(data['documentI'])}"
		payload = json.dumps(data)
		headers = {
		  'Content-Type': 'application/json',
		  'Accept': 'application/json',
		  'Authorization': 'Bearer 7692a20fec92af0aa5729d796b019d27c83c9955407994630a0cdd7702ca2329'
		}
		response = requests.request("POST", url, headers=headers, data=payload)
		print(response.text)
		return json.loads(response.text)['token']

	@classmethod
	def save_file(cls, data_file, name_file, path="media/Logo_Company/"):
		import base64
		import random
		_name_file = name_file.split(".")[-2]
		_ext = name_file.split(".")[-1]
		_name_file = _name_file+str(random.randint(100000, 999999))+"."+str(_ext)
		with open(path+_name_file, "wb") as file:
			file.write(base64.b64decode(bytes(data_file, "utf-8") + b'=='))
		return _name_file

	@classmethod
	def create_company(cls,data):
		result = False
		message = None
		pk = None
		try:
			#token = cls.create_company_api(cls,data)
			#if token:
			from user.models import Employee
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(token=data["token"])
				company = Company.objects.filter(pk = data["pk_company"]).first()
				#print(company)
				if not company:
					company = cls(
						documentI = data['documentI'],
						name = data['business_name'],
						name_commercial = data["name_commercial"],
						address = data['address'],
						phone = data['phone'],
						email = data['email'],
						type_document_identification = Type_Document_I.objects.filter(pk = data['type_document_identification_id']).first(),
						type_organization = Type_Organization.objects.filter(pk = data['type_organization_id']).first(),
						type_regime = Type_Regimen.objects.filter(pk = data['type_regime_id']).first(),
						municipality = Municipalities.objects.filter(pk = data['municipality_id']).first(),
						token = "",
						production = data['production'] if data['production'] is not None else False,
						software_company = data['id'],
						ping = data['pin'],
						sector = Sector.objects.filter(pk=data["sector"]).first(),
						site = data["site"],
						cant_employee = data["cant_employee"],
						money = data["money"],
						decimal = data["decimal"],
						point = data["point"]
					)

					company.save()
					result = True
					message = "Success"
					pk = company.pk
					data['pk_company'] = company.pk
					data_branch = Branch.create_branch(data)
					#result = Software.create_software(data,company)
					HistoryGeneral.create_history(
						action=HistoryGeneral.CREATED,
						class_models=HistoryGeneral.EMPRESA,
						class_models_json=json.loads(serializers.serialize('json', [company]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
					
				else:
					company.documentI = data['documentI']
					company.name = data['business_name']
					company.address = data['address']
					company.phone = data['phone']
					company.email = data['email']
					company.name_commercial = data["name_commercial"]
					company.type_document_identification = Type_Document_I.objects.filter(pk = data['type_document_identification_id']).first()
					company.type_organization = Type_Organization.objects.filter(pk = data['type_organization_id']).first()
					company.type_regime = Type_Regimen.objects.filter(pk = data['type_regime_id']).first()
					company.municipality = Municipalities.objects.filter(pk = data['municipality_id']).first()
					company.token = ""
					company.production = data['production'] if data['production'] is not None else False
					company.software_company = data['id']
					company.ping = data['pin']
					company.sector = Sector.objects.filter(pk=data["sector"]).first()
					company.site = data["site"]
					company.cant_employee = data["cant_employee"]
					company.money = data["money"]
					company.decimal = data["decimal"]
					company.point = data["point"]

					# Save logo
					_logo = ""
					if data["logo"] != None:
						_logo = cls.save_file(data["logo"], data["logo_name"])
						company.logo = "Logo_Company/"+_logo
						company.logo_b64 = data["logo"]
					#print(_logo)

					# save cer
					_cer = ""
					if data["cer"] != None:
						_cer = cls.save_file(data["cer"], data["cer_name"], "cert/")
						company.cer_file = "cert/"+_cer
					#print(_cer)

					# save key
					_key = ""
					if data["key"] != None:
						_key = cls.save_file(data["key"], data["key_name"], "cert/")
						company.key_file = "cert/"+_key
					#print(_key)
					company.pwd = data["pwd"]

					company.save()

					from invoice.finkok import FinkokService
					# get register client with finkok.
					finkok_service = FinkokService(rfc=company.documentI)
					resp = finkok_service.get_register_client()
					print(resp)
					if len(resp["users"]["ResellerUser"]) == 0:
						# register client from finkok.
						resp2 = finkok_service.register_client(str(company.cer_file), str(company.key_file), company.pwd)
						print(resp2)
					
					HistoryGeneral.create_history(
						action=HistoryGeneral.UPDATE,
						class_models=HistoryGeneral.EMPRESA,
						class_models_json=json.loads(serializers.serialize('json', [company]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
					result = True
					message = "Success"
					pk = company.pk
					data['pk_company'] = company.pk
					data_branch = {"pk_branch" :Branch.get_branch(data)["data"]["pk"]}
					#print(data_branch)
					
		except IntegrityError as inte:
			Branch.create_branch(data)
			message = f"Error IntegrityError Company {inte}"
		except Exception as e:
			message = str(e)
		#print(message)
		return {'result':result, 'message':message,'pk_company': pk, "pk_branch": data_branch["pk_branch"]}

	@classmethod
	def get_company(cls, data):
		from user.models import Employee
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			branch = Employee.search_by_token(token=data["token"]).branch
			result["data"] = json.loads(serializers.serialize('json', [branch.company]))[0]
			result["data"]["fields"]["regimen_data"] = json.loads(serializers.serialize('json', [branch.company.type_regime]))[0]["fields"] if branch.company.type_regime else {}
			#result["data"]['fields']['logo'] = env.URL_LOCAL + branch.company.logo.url
			result['code'] = 200
			result['message'] = "Success"
			result["status"] = "OK"
		return result

class Branch(models.Model):
	name = models.CharField(max_length=200)
	address = models.CharField(max_length = 150)
	phone = models.CharField(max_length = 15)
	email = models.EmailField()
	verified = models.BooleanField(default= False)
	company = models.ForeignKey(Company, on_delete= models.CASCADE)
	psswd = models.CharField(max_length = 10,default = get_random_string(length=10))
	value_coin = models.IntegerField(null= True, blank=True, default= 0)
	amount_min = models.IntegerField(null= True, blank=True, default= 0)
	municipality = models.ForeignKey(Municipalities, on_delete = models.CASCADE, null = True, blank = True)

	@classmethod
	def get_branch(cls, data):
		from user.models import Employee
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}	
		if Employee.check_by_token(token=data["token"]):
			branch = Employee.search_by_token(token=data["token"]).branch
			result["data"] = json.loads(serializers.serialize('json', [branch]))[0]
			result["data"]['fields']['logo'] = env.URL_LOCAL + branch.company.logo.url
			result['code'] = 200
			result['message'] = "Success"
			result["status"] = "OK"
		return result

	def __str__(self):
		return f"{self.name} - {self.company.name}"

	@classmethod
	def change_environment(cls, data):
		result = False
		message = None
		try:
			branch = cls.objects.get(pk = data['pk_branch'])
			payload = json.dumps({
			  "type_environment_id": data['type_environment'],
			  "payroll_type_environment_id": data['payroll_type_environment']
			})
			headers = {
			  'Authorization': f'Bearer {branch.company.token}',
			  'Content-Type': 'application/json',
			  'Accept': 'application/json'
			}
			response = requests.request("PUT", f'{env.URL_API}config/environment', headers=headers, data=payload)
			response = json.loads(response.text)
			message = response['message']
			result = True
			branch.company.production = True
			branch.company.save()
		except Exception as e:
			message = False
		return {'result':result,'message':message}

	@classmethod
	def list_branch(cls, data):
		result = {
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}	
		from user.models import Employee
		if Employee.check_by_token(token=data["token"]):
			_branch = Employee.search_by_token(token=data["token"]).branch
			for branch in Branch.objects.filter(company = _branch.company):
				a = json.loads(serializers.serialize('json', [branch]))[0]
				_a = a['fields']
				_a['pk'] = a['pk']
				result['data'].append(_a)

			result['code'] = 200
			result['message'] = "Success"
			result["status"] = "OK"
		return result

	@classmethod
	def create_branch(cls,data):
		result = False
		message = None
		try:
			branch = cls(
				name = data['business_name'],
				address = data['address'],
				phone = data['phone'],
				email = data['email'],
				municipality = Municipalities.objects.filter(pk = data['municipality_id']).first(),
				company = Company.objects.filter(pk = data['pk_company']).first()
			)
			branch.save()
			result = True
			message = "Success"
			#Resolution.create_resolution(data, branch)
			#result = Consecutive.create_consecutive(branch)
			result = License.create_license(data, branch)
			from customer.models import Customer as c
			c.create_consumidor_final(branch)
			from inventory.models import Supplier as s
			s.create_supplier_general(branch)

		except IntegrityError as inte:
			message = f"Error IntegrityError branch {inte}"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message, "pk_branch": branch.pk}


	@staticmethod
	def GenerateIMG(img_base64, name):
		try:
			image_data = base64.b64decode(img_base64)
			image_stream = BytesIO(image_data)
			image_filename = f"{name}.jpg"
			return (image_filename, image_stream)
		except Exception as e:
			print(e)
			return {'result':False}

	@classmethod
	def update_logo(cls, data):
		result = False
		message = None
		url_logo = None
		try:
			branch = cls.objects.get(pk = data['pk_branch'])
			image_filename, image_stream = cls.GenerateIMG(data['logo'], branch.name)
			branch.company.logo.save(image_filename, image_stream)			
			branch.company.save()
			result = True
			message = "Success"
			url_logo = env.URL_LOCAL + branch.company.logo.url
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message, 'url_logo': url_logo}


	@classmethod
	def update_branch(cls, data):
		result = False
		message = None
		try:
			
			branch = cls.objects.get(pk = data['pk_branch'])
			
			branch.name = data['business_name']
			branch.address = data['address']
			branch.phone = data['phone']
			branch.email = data['email']
			branch.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

	@classmethod
	def add_branch(cls,data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}	
		try:
			from user.models import Employee
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(token=data["token"])
				_branch = employee.branch
				branch = cls.objects.filter(pk = data["pk_branch"]).first()
				if not branch:
					branch = cls(
						name = data['business_name'],
						address = data['address'],
						phone = data['phone'],
						email = data['email'],
						company = _branch.company
					)
					branch.save()
					result = License.create_license(data, branch)
					#Resolution.create_resolution(data, branch)
					from customer.models import Customer as c
					c.create_consumidor_final(branch)
					from inventory.models import Supplier as s
					s.create_supplier_general(branch)
					HistoryGeneral.create_history(
						action=HistoryGeneral.CREATED,
						class_models=HistoryGeneral.BRANCH,
						class_models_json=json.loads(serializers.serialize('json', [branch]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
				else:
					branch.name = data['business_name']
					branch.address = data['address']
					branch.phone = data['phone']
					branch.email = data['email']
					branch.save()

					HistoryGeneral.create_history(
						action=HistoryGeneral.UPDATE,
						class_models=HistoryGeneral.BRANCH,
						class_models_json=json.loads(serializers.serialize('json', [branch]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)

				result['code'] = 200
				result["status"] = "OK"
				result["message"] = "Success"
		except Exception as e:
			result["message"] = str(e)
		return result

	@classmethod
	def delete_branch(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}	
		try:
			from user.models import Employee
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(token=data["token"])
				branch = cls.objects.filter(pk = data["pk_branch"]).first()
				HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.BRANCH,
					class_models_json=json.loads(serializers.serialize('json', [branch]))[0],
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				branch.delete()
				result['code'] = 200
				result["status"] = "OK"
				result["message"] = "Success"
		except Exception as e:
			result["message"] = str(e)
		return result


class Store(models.Model):
	name = models.CharField(max_length=200)
	address = models.CharField(max_length = 150)
	description = models.TextField()
	branch = models.ForeignKey(Branch, on_delete= models.CASCADE)

	@classmethod
	def get_store(cls, data):
		from user.models import Employee
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}	
		if Employee.check_by_token(token=data["token"]):
			store = cls.objects.filter(pk = data["pk_store"])
			result["data"] = json.loads(serializers.serialize('json', [store]))[0]
			result['code'] = 200
			result['message'] = "Success"
			result["status"] = "OK"
		return result

	def __str__(self):
		return f"{self.name} - {self.branch.name}"

	@classmethod
	def list_store(cls, data):
		result = {
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}	
		from user.models import Employee
		if Employee.check_by_token(token=data["token"]):
			_branch = Employee.search_by_token(token=data["token"]).branch
			for store in cls.objects.filter(branch = _branch):
				a = json.loads(serializers.serialize('json', [store]))[0]
				_a = a['fields']
				_a['pk'] = a['pk']
				result['data'].append(_a)

			result['code'] = 200
			result['message'] = "Success"
			result["status"] = "OK"
		return result

	@classmethod
	def add_store(cls,data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}	
		try:
			from user.models import Employee
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(token=data["token"])
				_branch = employee.branch
				store = cls.objects.filter(pk = data["pk_store"]).first()
				if not store:
					store = cls(
						name = data['store_name'],
						address = data['address'],
						description = data['description'],
						branch = _branch
					)
					store.save()
					HistoryGeneral.create_history(
						action=HistoryGeneral.CREATED,
						class_models=HistoryGeneral.STORE,
						class_models_json=json.loads(serializers.serialize('json', [store]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
				else:
					store.name = data['store_name']
					store.address = data['address']
					store.description = data['description']
					store.save()

					HistoryGeneral.create_history(
						action=HistoryGeneral.UPDATE,
						class_models=HistoryGeneral.STORE,
						class_models_json=json.loads(serializers.serialize('json', [store]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)

				result['code'] = 200
				result["status"] = "OK"
				result["message"] = "Success"
		except Exception as e:
			result["message"] = str(e)
		return result

	@classmethod
	def delete_store(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}	
		try:
			from user.models import Employee
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(token=data["token"])
				store = cls.objects.filter(pk = data["pk_store"]).first()
				HistoryGeneral.create_history(
					action=HistoryGeneral.UPDATE,
					class_models=HistoryGeneral.STORE,
					class_models_json=json.loads(serializers.serialize('json', [store]))[0],
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				store.delete()
				result['code'] = 200
				result["status"] = "OK"
				result["message"] = "Success"
		except Exception as e:
			result["message"] = str(e)
		return result


from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta, date

class Resolution(models.Model):
	type_document_id = models.IntegerField()
	prefix = models.CharField(max_length = 7)
	resolution = models.IntegerField(null = True, blank = True)
	resolution_date = models.CharField(max_length = 10, null = True, blank = True)
	technical_key = models.CharField(max_length = 255, null = True, blank = True)
	_from = models.IntegerField()
	_to = models.IntegerField()
	generated_to_date = models.IntegerField(default = 0, null = True, blank = True)
	date_from = models.CharField(max_length = 10, null = True, blank = True)
	date_to = models.CharField(max_length = 10, null = True, blank = True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)

	def __str__(self):
		return f"Prefix: {self.prefix}, Type Document {self.type_document_id} -  by {self.branch.name}"

	@classmethod
	def get_number(cls, type_document):
		return cls.objects.get(type_document_id = type_document)._from


	@classmethod
	def update_resolution_dian(cls,data):
		result = False
		message = None
		branch = Branch.objects.get(pk = data['pk_branch'])
		url = f"{env.URL_API}/numbering-range"
		payload = json.dumps({
		  "NIT": branch.company.documentI,
		  "IDSoftware": branch.company.software_company
		})
		headers = {
		  'Content-Type': 'application/json',
		  'accept': 'application/json',
		  'Authorization': f'Bearer {branch.company.token}'
		}
		response = requests.request("POST", url, headers= headers, data=payload)
		_data = json.loads(response.text)["ResponseDian"]["Envelope"]["Body"]["GetNumberingRangeResponse"]["GetNumberingRangeResult"]["ResponseList"]["NumberRangeResponse"]
		if isinstance(_data, list):
			for i in _data:
				if int(data['resolution']) == int(i['ResolutionNumber']):
					_data = i
					break
		try:
			r = cls.objects.get(type_document_id = data['type_document_id'], branch = branch)
			r.type_document_id = data['type_document_id']
			r.prefix = _data['Prefix']
			r.resolution = _data['ResolutionNumber']
			r.resolution_date = _data['ResolutionDate']
			r.technical_key = _data['TechnicalKey']
			r._from = _data['FromNumber']
			r._to = _data['ToNumber']
			r.date_from = _data['ValidDateFrom']
			r.date_to = _data['ValidDateTo']
			result = True
			r.message = "Success"
			_data = json.loads(serializers.serialize('json', [r]))[0]
			_data = _data['fields']
			_data['pk_branch'] = branch.pk
			_data['from'] = _data['_from']
			_data['to'] = _data['_to']
			r.save()
			cls.update_resolution(_data)
		except cls.DoesNotExist as e:
			message = str(e)
			_data = []
		return {'result':result,'data':_data}


	@classmethod
	def get_resolution(cls, data):
		value = None
		try:
			resolution = cls.objects.get(type_document_id = data['type_document'], branch = Branch.objects.get(pk = data['pk_branch']))
			value = json.loads( serializers.serialize('json', [resolution]))[0]['fields']
			to_date  = datetime.strptime(value['date_to'], '%Y-%m-%d')
			current_date = datetime.now()
			date_difference =  to_date - current_date
			value['date_valid'] = False
			value['days_expiration'] = f"Su resolución vencerá en {str(date_difference.days).replace('-','')} días."
			value['days_expiration_resolution'] = date_difference.days
			if date_difference.days < 0:
				value['date_valid'] = True
				value['days_expiration'] = f"Su resolución esta vencidad desde hace {str(date_difference.days).replace('-','')} días."
			if date_difference.days == 0:
				value['date_valid'] = True
				value['days_expiration'] = f"Su resolución se vencio el día de hoy."
		except cls.DoesNotExist as e:
			value = {}
		return value

	@classmethod
	def get_resolution_list(cls, data):
		value = None
		try:
			resolution = cls.objects.filter(branch = Branch.objects.get(pk = data['pk_branch']))
			value = []
			for i in resolution:
				if i.type_document_id != 98:
					data = json.loads(serializers.serialize('json', [i]))[0]
					data['from'] = data['fields']['_from']
					data['to'] = data['fields']['_to']
					data['resolution'] = data['fields']['resolution']
					try:
						to_date  = datetime.strptime(data['fields']['date_to'], '%Y-%m-%d')
						current_date = datetime.now()
						date_difference =  to_date - current_date
						data['date_difference'] = date_difference
					except Exception as ex:
						print(ex)
					value.append(data)
		except cls.DoesNotExist as e:
			value = {}
		return value

	@classmethod
	def add_number(cls, data):
		resolution = cls.objects.get(type_document_id = data['type_document'], branch = Branch.objects.get(pk = data['pk_branch']))
		result = False
		message = None
		if resolution._from <= resolution._to:
			resolution._from += 1
			resolution.save()
			result = True
			message = "Success"
		else:
			message = "Ya ha consumido todo el rango de numeración de su resolución, se le informa que debe generar otra resolución"
		return {'result':result, 'message':message}

	@classmethod
	def create_resolution(cls,data, branch):
		result = False
		message = None
		try:
			r = cls.objects.get(type_document_id = data['type_document_id'], branch = branch)
			r.type_document_id = data['type_document_id']
			r.prefix = data['prefix']
			r.resolution = data['resolution']
			r.resolution_date = data['resolution_date']
			r.technical_key = data['technical_key']
			r._from = data['from']
			r._to = data['to']
			r.date_from = data['date_from']
			r.date_to = data['date_to']
			result = True
			r.message = "Success"
			r.save()
		except cls.DoesNotExist as e:
			resolution = cls(
				type_document_id = data['type_document_id'],
				prefix = data['prefix'],
				resolution = data['resolution'],
				resolution_date = data['resolution_date'],
				technical_key = data['technical_key'],
				_from = data['from'],
				_to = data['to'],
				date_from = data['date_from'],
				date_to = data['date_to'],
				branch = branch,
			)
			resolution.save()
			result = True
			message = "Success"

		if result:
			result = cls.create_resolution_api(data, branch)
		return {'result':result, 'message':message}

	@staticmethod
	def create_resolution_api(data, branch):
		result = False
		message = None
		try:
			if data['type_document_id'] != 98:
				_url = Operation.objects.get(pk = 1).url_api
				url = f"{_url}/api/ubl2.1/config/resolution"
				payload = json.dumps(data)
				headers = {
				  'Content-Type': 'application/json',
				  'accept': 'application/json',
				  'Authorization': 'Bearer '+str(branch.company.token)
				}
				response = requests.request("PUT", url, headers=headers, data=payload)
				print(response.text)
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

	@classmethod
	def update_resolution(cls,data):
		result = False
		message = None
		try:
			branch = Branch.objects.get(pk = data['pk_branch'])
			resolution = cls.objects.get(type_document_id=data['type_document_id'], branch = branch) 
			resolution.type_document_id = data['type_document_id']
			resolution.prefix = data['prefix']
			resolution.resolution = data['resolution']
			resolution.resolution_date = data['resolution_date']
			resolution.technical_key = data['technical_key']
			resolution._from = data['from']
			resolution._to = data['to']
			resolution.date_from = data['date_from']
			resolution.date_to = data['date_to']
			resolution.save()
			return cls.create_resolution_api(data, branch)
		except cls.DoesNotExist as e:
			message = str(e)
		return {'result': result, 'message': message}


class Software(models.Model):
	_id = models.CharField(max_length = 100)
	pin = models.IntegerField()
	company = models.ForeignKey(Company, on_delete = models.CASCADE)

	def __str__(self):
		return self.company.name

	@staticmethod
	def update_software_api(data,token):
		_url = Operation.objects.get(pk = 1).url_api
		url = f"{_url}/api/ubl2.1/config/software"
		payload = json.dumps(data)
		headers = {
		  'Content-Type': 'application/json',
		  'cache-control': 'no-cache',
		  'Connection': 'keep-alive',
		  'Accept-Encoding': 'gzip, deflate',
		  'accept': 'application/json',
		  'X-CSRF-TOKEN': '',
		  'Authorization': 'Bearer '+str(token)
		}
		response = requests.request("PUT", url, headers=headers, data=payload)
		return json.loads(response.text)["success"]

	@classmethod
	def create_software(cls,data,company):
		result = False
		message = None
		try:
			r = cls.update_software_api(data,company.token)
			print(r)
			if r:
				software = cls(
					_id = data['id'],
					pin = data['pin'],
					company = company
				)
				software.save()
				result = True
				message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}


class SerieFolio(models.Model):
	TYPE_DOCUMENT_CHOICES = (
	    ('Factura de venta', 'Factura de venta'),
	    ('Ticket de venta', 'Ticket de venta'),
	    ('Ajuste de inventario', 'Ajuste de inventario'),
	    ('Factura de traslado', 'Factura de traslado'),
	)
	type_document = models.CharField(max_length=30, choices=TYPE_DOCUMENT_CHOICES,null = True, blank = True)
	name = models.CharField(max_length=100)
	serie_folio_auto = models.BooleanField(default=True)
	serie = models.CharField(max_length=30)
	folio_from = models.IntegerField()
	folio_to = models.IntegerField()
	preferida = models.BooleanField(default=True)
	pie_invoice = models.TextField()
	next_folio = models.IntegerField(default=1)
	state = models.BooleanField(default=True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)

	def __str__(self) -> str:
		return str(self.type_document)+" | From: "+str(self.folio_from)+" | To: "+str(self.folio_to)
	
	@classmethod
	def create_serie_folio(cls, data):
		from user.models import Employee
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			employee = Employee.search_by_token(token=data["token"])
			try:
				serie_folio = cls.objects.filter(pk = data["pk"]).first()
				if not serie_folio:
					serie_folio = cls.objects.create(
						type_document = data["type_document"],
						name = data["name"],
						serie_folio_auto = data["serie_folio_auto"],
						serie = data["serie"],
						folio_from = data["folio_from"],
						folio_to = data["folio_to"],
						preferida = data["preferida"],
						pie_invoice = data["pie_invoice"],
						state = data["state"],
						next_folio = data["folio_from"],
						branch = employee.branch
					)
					HistoryGeneral.create_history(
                        action=HistoryGeneral.CREATED,
                        class_models=HistoryGeneral.RESOLUTION,
                        class_models_json=json.loads(serializers.serialize('json', [serie_folio]))[0],
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
				else:
					serie_folio.name = data["name"]
					serie_folio.type_document = data["type_document"]
					serie_folio.serie_folio_auto = data["serie_folio_auto"]
					serie_folio.serie = data["serie"]
					serie_folio.folio_from = data["folio_from"]
					serie_folio.folio_to = data["folio_to"]
					serie_folio.preferida = data["preferida"]
					serie_folio.pie_invoice = data["pie_invoice"]
					#serie_folio.next_folio = data["folio_from"]
					serie_folio.state = data["state"]

					HistoryGeneral.create_history(
                        action=HistoryGeneral.UPDATE,
                        class_models=HistoryGeneral.RESOLUTION,
                        class_models_json=json.loads(serializers.serialize('json', [serie_folio]))[0],
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
				serie_folio.save()
				result["code"] = 200
				result["status"] = "OK"
				result["message"] = "Success"
			except IntegrityError as e:
				result["message"] = str(e)
		return result
	@classmethod
	def get_list_serie_folio(cls, data):
		from user.models import Employee
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
            "data": []
		}
		if Employee.check_by_token(token=data["token"]):
			employee = Employee.search_by_token(token=data["token"])
			result["data"] =  [
                {
                    "type_document":i.type_document,
					"name":i.name,
					"serie_folio_auto":i.serie_folio_auto,
					"serie":i.serie,
					"folio_from":i.folio_from,
					"folio_to":i.folio_to,
					"preferida":i.preferida,
					"pie_invoice":i.pie_invoice,
					"state":i.state,
					"branch":i.branch.pk,
					"next_folio":i.next_folio,
					"pk":i.pk
                }
                for i in cls.objects.filter(branch=employee.branch).order_by("-id")
            ]
			result["code"] = 200
			result["status"] = "OK"
			result["message"] = "Success"
		return result
	
	@classmethod
	def delete_serie_folio(cls, data):
		from user.models import Employee
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(token=data["token"])
				_serie_folio = cls.objects.filter(pk = data["pk"])
				HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.RESOLUTION,
					class_models_json=json.loads(serializers.serialize('json', [_serie_folio.first()]))[0],
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				_serie_folio.delete()
				result["code"] = 200
				result["message"] = "Success"
				result["status"] = "OK"
		except IntegrityError as e:
			result["message"] = str(e)
		return result
	
	@classmethod
	def get_serie_folio(cls, data):
		from user.models import Employee
		result = {
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(token=data["token"])
				_serie_folio = cls.objects.filter(type_document = data["type_document"], branch=employee.branch)
				if _serie_folio:
					for sf in _serie_folio:
						result["data"].append({
							"type_document":sf.type_document,
							"name":sf.name,
							"serie_folio_auto":sf.serie_folio_auto,
							"serie":sf.serie,
							"folio_from":sf.folio_from,
							"folio_to":sf.folio_to,
							"preferida":sf.preferida,
							"pie_invoice":sf.pie_invoice,
							"state":sf.state,
							"branch":sf.branch.pk,
							"next_folio":sf.next_folio,
							"pk":sf.pk
						})
					result["code"] = 200
					result["message"] = "Success"
					result["status"] = "OK"
				else:
					result["code"] = 400
					result["message"] = "Folio no encontrado"
					result["status"] = "Fail"
		except Exception as e:
			result["message"] = str(e)
		return result

	@classmethod
	def increment_serie_folio(cls, data):
		from user.models import Employee
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(token=data["token"])
				_serie_folio = cls.objects.filter(pk=data["pk"]).first()
				if _serie_folio:
					_serie_folio.next_folio += 1
					_serie_folio.save()
					result["code"] = 200
					result["message"] = "Success"
					result["status"] = "OK"
				else:
					result["code"] = 400
					result["message"] = "Folio no encontrado"
					result["status"] = "Fail"
		except Exception as e:
			result["message"] = str(e)
		return result

class Consecutive(models.Model):
	pos = models.IntegerField(default = 1) # caja
	elec = models.IntegerField(default = 1) # electronica
	nc = models.IntegerField(default = 1) # nota credito
	nd = models.IntegerField(default = 1) # nota debito
	ni = models.IntegerField(default = 1) # nota ingreso
	ne = models.IntegerField(default = 1) # nota egreso
	rm = models.IntegerField(default = 1) # remission
	ct = models.IntegerField(default = 1) # cotizacion
	oc = models.IntegerField(default = 1) # orden de compra
	se = models.IntegerField(default = 1) # servicio
	tras = models.IntegerField(default = 1) # traslado
	branch = models.OneToOneField(Branch, on_delete = models.CASCADE)

	def __str__(self):
		return self.branch.name

	@classmethod
	def create_consecutive(cls, data):
		from user.models import Employee
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(token=data["token"])
				cons = cls.objects.filter(branch = employee.branch).first()
				if not cons:
					cons = cls.objects.create(branch=employee.branch)
					HistoryGeneral.create_history(
						action=HistoryGeneral.CREATED,
						class_models=HistoryGeneral.RESOLUTION,
						class_models_json=json.loads(serializers.serialize('json', [cons]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
				else:
					cons.pos = data["pos"]
					#cons.elec = data["elec"]
					cons.nc = data["nc"]
					#cons.nd = data["nd"]
					cons.ni = data["ni"]
					cons.ne = data["ne"]
					cons.rm = data["rm"]
					cons.ct = data["ct"]
					cons.oc = data["oc"]
					cons.se = data["se"]
					#cons.pos = data["tras"]
					cons.save()

					HistoryGeneral.create_history(
						action=HistoryGeneral.UPDATE,
						class_models=HistoryGeneral.RESOLUTION,
						class_models_json=json.loads(serializers.serialize('json', [cons]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
				result["code"] = 200
				result["message"] = "Success"
				result["status"] = "OK"
		except IntegrityError as e:
			result["message"] = str(e)
		return result

	@classmethod
	def consecutive_increment(cls, type_document, branch):
		cons = cls.objects.filter(branch=branch).first()
		if type_document == "rm":
			cons.rm += 1
		elif type_document == "pos":
			cons.pos += 1
		elif type_document == "nc":
			cons.nc += 1
		elif type_document == "nd":
			cons.nd += 1
		elif type_document == "ne":
			cons.ne += 1
		elif type_document == "ni":
			cons.ni += 1
		elif type_document == "ct":
			cons.ct += 1
		elif type_document == "oc":
			cons.oc += 1	
		elif type_document == "se":
			cons.se += 1	
		elif type_document == "tras":
			cons.tras += 1	
		cons.save()
	
	@classmethod
	def get_consecutive(cls, data):
		from user.models import Employee
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(token=data["token"])
				consecutive = cls.objects.filter(branch=employee.branch).first()
				if not consecutive:
					consecutive = cls.create_consecutive(data)
				result["data"] = json.loads(serializers.serialize('json', [consecutive]))[0]["fields"]
				result["data"]["pk"] = consecutive.pk
				result["code"] = 200
				result["message"] = "Success"
				result["status"] = "OK"
		except Exception as e:
			result["message"] = str(e)
		return result
	
class License(models.Model):
	price = models.IntegerField(null = True, blank = True)
	document = models.IntegerField(null = True, blank = True)
	user = models.IntegerField(null = True, blank = True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE, null = True, blank = True)
	date_registration = models.DateField(auto_now_add = True, null = True, blank = True)
	expiration_date = models.CharField(max_length = 12, null = True, blank = True)

	def __str__(self):
		return f'Branch: {self.branch.name} - Company: {self.branch.company.name}'

	@staticmethod
	def packages(obj):
		data = {}
		if obj.price == 0:
			data = {
				'document':12,
				'user':1,
				'expiration_date': obj.date_registration  + timedelta(days=365)
			}
		elif obj.price == 62500:
			data = {
				'document':750,
				'user':1,
				'expiration_date': obj.date_registration  + relativedelta(months=1)
			}
		elif obj.price == 84000:
			data = {
				'document':1500,
				'user':1,
				'expiration_date': obj.date_registration  + relativedelta(months=1)
			}
		elif obj.price == 209000:
			data = {
				'document':6000,
				'user':3,
				'expiration_date': obj.date_registration  + relativedelta(months=1)
			}
		elif obj.price == 225000:
			data = {
				'document':12000,
				'user':5,
				'expiration_date': obj.date_registration  + relativedelta(months=1)
			}
		elif obj.price == 2100000:
			data = {
				'document':80000000,
				'user': 300,
				'expiration_date': obj.date_registration  + timedelta(days=365)
			}
		return data

	@classmethod
	def create_license(cls, data, branch):
		result = False
		message = None
		try:
			license = cls(
				price = data['price']
			)
			license.save()
			p = cls.packages(license)
			license.document = p['document']
			license.user = p['user']
			license.branch = branch
			license.expiration_date = p['expiration_date']
			license.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}


	@classmethod
	def validate_date(cls,branch):
		license = cls.objects.get(branch = branch).expiration_date
		license_date  = datetime.strptime(license, '%Y-%m-%d')
		current_date = datetime.now()
		date_difference = license_date - current_date
		days_until_expiration = abs(date_difference.days)
		message = None
		result = False
		if date_difference.days < 0:
			message = "Su licencia esta expirada"
		else:
			result = True
			message = "Success"
		print(message)
		return {'result':result, 'message': message}
		
	@classmethod
	def update_date_license(cls, data):
		result = False
		message = None
		try:
			license = cls.objects.get(branch = Branch.objects.get(pk = data['pk_branch']))
			__date = date.today() + timedelta(days=365) if license.price == 0 or license.price == 2300000 else date.today() + relativedelta(months=1)
			license.expiration_date = __date
			license.document = cls.packages(license)['document']
			license.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message': message}


	@classmethod
	def add_user(cls,branch):
		result = False
		message = None
		try:
			license = cls.objects.get(branch = branch)
			license.user += 1
			license.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

	@classmethod
	def discount_user(cls,branch):
		result = False
		message = None
		try:
			license = cls.objects.get(branch = branch)
			if license.user > 0:
				license.user -= 1
				license.save()
				result = True
				message = "Success"
			else:
				message = "Ya no tiene más usuarios disponibles"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

	@classmethod
	def discount_license(cls, branch):
		result = False
		message = None
		try:
			license = cls.objects.get(branch = branch)
			if license.document > 0:
				license.document -= 1
				license.save()
				result = True
				message = "Success"
			else:
				message = "Ya no tiene más documentos electrónicos disponibles"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}


class Bank(models.Model):
	BANK_NATIONAL = 'Banco nacional'
	CREDIT_CARD = 'Tarjeta de credito'
	EFECTIVO = 'Efectivo'
	FOREING_BANK = "Banco extranjero"
	TYPE_ACCOUNT = (
	    (BANK_NATIONAL, BANK_NATIONAL),
	    (CREDIT_CARD, CREDIT_CARD),
	    (EFECTIVO, EFECTIVO),
	    (FOREING_BANK, FOREING_BANK),
	)
	type_account = models.CharField(max_length=30, choices=TYPE_ACCOUNT, default=BANK_NATIONAL)
	name = models.CharField(max_length=512)
	account_number = models.CharField(max_length=512)
	amount_init = models.FloatField()
	amount = models.FloatField()
	date_amount_init = models.DateField()
	description = models.TextField()
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	NOT_CONNECT = "No conectado"
	STATUS = (
	    (NOT_CONNECT, NOT_CONNECT),
	)
	state = models.CharField(max_length=30, choices=STATUS, default=NOT_CONNECT)

	def __str__(self) -> str:
		return str(self.branch)+" | name: "+str(self.name)+" | number: "+str(self.account_number)
	
	@classmethod
	def create_bank(cls, data):
		from user.models import Employee
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			employee = Employee.search_by_token(token=data["token"])
			try:
				bank = cls.objects.filter(pk = data["pk"]).first()
				if not bank:
					bank = cls.objects.create(
						type_account = data["type_account"],
						name = data["name"],
						account_number = data["account_number"],
						amount_init = data["amount_init"],
						amount = data["amount_init"],
						date_amount_init = data["date_amount_init"],
						description = data["description"],
						branch = employee.branch
					)
					_bank_json = {
						"type_account": bank.type_account,
						"name": bank.name,
						"account_number": bank.account_number,
						"amount_init": bank.amount_init,
						"amount": bank.amount,
						"date_amount_init": str(bank.date_amount_init),
						"description": bank.description,
						"branch": str(bank.branch),
					}
					HistoryGeneral.create_history(
                        action=HistoryGeneral.CREATED,
                        class_models=HistoryGeneral.BANK,
                        class_models_json=_bank_json,
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
				else:
					bank.name = data["name"]
					bank.type_account = data["type_account"]
					bank.account_number = data["account_number"]
					bank.amount_init = data["amount_init"]
					bank.amount = data["amount_init"]
					bank.date_amount_init = data["date_amount_init"]
					bank.description = data["description"]
					
					_bank_json = {
						"type_account": bank.type_account,
						"name": bank.name,
						"account_number": bank.account_number,
						"amount_init": bank.amount_init,
						"amount": bank.amount,
						"date_amount_init": str(bank.date_amount_init),
						"description": bank.description,
						"branch": str(bank.branch),
					}

					HistoryGeneral.create_history(
                        action=HistoryGeneral.UPDATE,
                        class_models=HistoryGeneral.BANK,
                        class_models_json=_bank_json,
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
				bank.save()
				result["code"] = 200
				result["status"] = "OK"
				result["message"] = "Success"
			except IntegrityError as e:
				result["message"] = str(e)
		return result
	@classmethod
	def get_list_bank(cls, data):
		from user.models import Employee
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
            "data": [],
			"type_account": []
		}
		if Employee.check_by_token(token=data["token"]):
			employee = Employee.search_by_token(token=data["token"])
			from inventory.models import Product
			result["type_account"] =  [
                {
					"name":i[0]
                }
                for i in cls.TYPE_ACCOUNT
            ]
			result["data"] =  [
                {
                    "type_account":i.type_account,
					"name":i.name,
					"account_number":i.account_number,
					"amount_init":i.amount_init,
					"date_amount_init":i.date_amount_init,
					"description":i.description,
					"balance":i.amount,
					"balance_money":Product.format_price(i.amount),
					"state":i.state,
					"pk":i.pk
                }
                for i in cls.objects.filter(branch=employee.branch).order_by("-id")
            ]
			result["code"] = 200
			result["status"] = "OK"
			result["message"] = "Success"
		return result
	
	@classmethod
	def delete_bank(cls, data):
		from user.models import Employee
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(token=data["token"])
				bank = cls.objects.filter(pk = data["pk"])
				HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.BANK,
					class_models_json=json.loads(serializers.serialize('json', [bank.first()]))[0],
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				bank.delete()
				result["code"] = 200
				result["message"] = "Success"
				result["status"] = "OK"
		except IntegrityError as e:
			result["message"] = str(e)
		return result
	
	@classmethod
	def get_bank(cls, data):
		from user.models import Employee
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(token=data["token"])
				from inventory.models import Product
				bank = cls.objects.filter(pk = data["pk"], branch=employee.branch).first()
				if bank:
					result["data"] = {
						"type_account":bank.type_account,
						"name":bank.name,
						"account_number":bank.account_number,
						"amount_init":bank.amount_init,
						"balance":bank.amount,
						"balance_money":Product.format_price(bank.amount),
						"date_amount_init":bank.date_amount_init,
						"description":bank.description,
						"branch":bank.branch,
						"pk":bank.pk
					}
					result["code"] = 200
					result["message"] = "Success"
					result["status"] = "OK"
				else:
					result["code"] = 400
					result["message"] = "Banco no encontrado"
					result["status"] = "Fail"
		except Exception as e:
			result["message"] = str(e)
		return result