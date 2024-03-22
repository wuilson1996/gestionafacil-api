from django.http import JsonResponse
from django.core import serializers
from django.db import IntegrityError
from company.models import Branch
from django.db.models import Sum
from user.models import Employee
from django.db import models
from setting.models import *
from datetime import date as _date
import json

class Supplier(models.Model):
	documentI = models.CharField(max_length=50, null = True, blank = True)
	name = models.CharField(max_length = 70)
	email = models.EmailField(null = True, blank = True)
	phone = models.CharField(max_length = 15,null = True, blank = True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	address = models.TextField(null = True, blank = True)
	merchant_registration = models.CharField(max_length = 30,null = True, blank = True)
	postal_zone_code = models.IntegerField(null = True, blank = True)
	type_document_identification_id = models.ForeignKey(Type_Document_I, on_delete = models.CASCADE,null = True, blank = True)
	municipality_id = models.ForeignKey(Municipalities, on_delete = models.CASCADE,null = True, blank = True)
	type_liability_id = models.IntegerField(null = True, blank = True)
	type_regime_id = models.ForeignKey(Type_Regimen, on_delete = models.CASCADE, null = True, blank = True)


	def __str__(self):
		return f"{self.name} by {self.branch.name}"

	@classmethod
	def create_supplier(cls,data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			#print("Create supplier")
			#print(data)
			if Employee.check_by_token(data["token"]):
				branch = Employee.search_by_token(token=data["token"]).branch
				supplier = cls.objects.filter(pk = data['pk_supplier'] if data["pk_supplier"] != "" else 0, branch = branch).first()
				if not supplier:
					supplier = cls(
						documentI = data['identification_number'],
						name = data['name'],
						email = data['email'],
						phone = data['phone'],
						address = data['address'] if data['address'] else None,
						municipality_id = Municipalities.objects.filter(pk = data['municipality_id']).first(),
						type_regime_id = Type_Regimen.objects.filter(pk = data['type_regime_id']).first(),
						branch = branch
					)
					supplier.save()
					if data['associate_person']:
						Associate_Person.create_associate_person(data['associate_person'], supplier)
					if data['commercial_information']:
						Commercial_Information.create_commercial_information(data['commercial_information'], supplier)
				else:
					supplier.documentI = data['identification_number']
					supplier.name = data['name']
					supplier.phone = data['phone'] if data['phone'] else None
					supplier.address = data['address'] if data['address'] else None
					supplier.email = data['email'] if data['email'] else None
					supplier.municipality_id = Municipalities.objects.filter(pk = data['municipality_id']).first()
					supplier.type_regime_id = Type_Regimen.objects.filter(pk = data['type_regime_id']).first()
					supplier.save()
					#if data['associate_person']:
					Associate_Person.create_associate_person(data['associate_person'], supplier)
					#if data['commercial_information']:
					Commercial_Information.create_commercial_information(data['commercial_information'], supplier)

				result['code'] = 200
				result['status'] = 'OK'
				result['message'] = "Success"
		except Exception as e:
			result['message'] = str(e)
		return result


	@classmethod
	def create_supplier_general(cls, branch):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			supplier = cls(
				name = "Proveedor General",
				branch = branch
			)
			supplier.save()
			result['code'] = 200
			result['status'] = 'OK'
			result['message'] = "Success"
		except Exception as e:
			result['message'] = str(e)
		return result

	@classmethod
	def update_supplier(cls,data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(data["token"]):
				supplier = cls.objects.get(pk = data['pk_supplier'])
				supplier.documentI = data['documentI']
				supplier.name = data['name']
				supplier.email = data['email']
				supplier.phone = data['phone']
				supplier.save()
				result['code'] = 200
				result['status'] = 'OK'
				result['message'] = "Success"
		except Exception as e:
			result['message'] = str(e)
		return result

	@staticmethod
	def serializers_data(obj):
		serialized_supplier = serializers.serialize('json', [obj])
		return json.loads(serialized_supplier)[0]

	@classmethod
	def list_supplier(cls, data):
		result = {
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			branch = Employee.search_by_token(token=data["token"]).branch
			for i in cls.objects.filter(branch = branch):
				supplier = cls.serializers_data(i)
				data = supplier['fields']
				data['pk'] = supplier['pk']
				data['name_type_regime'] = Type_Regimen.objects.filter(id=supplier["fields"]["type_regime_id"]).first().name if Type_Regimen.objects.filter(id=supplier["fields"]["type_regime_id"]).first() else ""
				data["associate_person"] = Associate_Person.get_data(supplier=data['pk'])
				data["commercial_information"] = Commercial_Information.get_data(supplier=data['pk'])
				result['data'].append(data)
			result['code'] = 200
			result['status'] = 'OK'
			result['message'] = "Success"
		
		#print(result)
		return result

	@classmethod
	def get_supplier(cls,data):
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			try:
				#print(data)
				result["data"] = json.loads( serializers.serialize('json', [cls.objects.get(pk = data['pk_supplier'])]))[0]['fields']
				result["data"]["pk"] = data['pk_supplier']
				result["data"]['name_type_regime'] = Type_Regimen.objects.filter(id=result["data"]["type_regime_id"]).first().name if Type_Regimen.objects.filter(id=result["data"]["type_regime_id"]).first() else ""
				result["data"]["associate_person"] = Associate_Person.get_data(supplier=data['pk_supplier'])
				result["data"]["commercial_information"] = Commercial_Information.get_data(supplier=data['pk_supplier'])
				result['code'] = 200
				result['status'] = 'OK'
				result['message'] = "Success"
			except Exception as e:
				result["message"] = str(e)
		
		#print(result)
		return result

	@classmethod
	def delete_supplier(cls,data):
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = employee = Employee.search_by_token(data['token']).branch
				cls.objects.get(branch = branch, pk = data['pk_suppplier']).delete()
				result['code'] = 200
				result['status'] = 'OK'
				result['message'] = "Success"
		except Exception as e:
			result['message'] = str(e)
		return result

class Associate_Person(models.Model):
	name = models.CharField(max_length = 50)
	last_name = models.CharField(max_length = 50)
	email = models.EmailField()
	phone_1 = models.CharField(max_length = 15)
	phone_2 = models.CharField(max_length = 15)
	supplier = models.ForeignKey(Supplier, on_delete = models.CASCADE)

	def __str__(self):
		return f'{self.name} {self.last_name} by {self.supplier.name}'

	@classmethod
	def create_associate_person(cls, data, supplier):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			for ap in cls.objects.filter(supplier=supplier):
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
							supplier = supplier
						)
						associate_person.save()
					else:
						associate_person.name = i['name']
						associate_person.last_name = i['last_name']
						associate_person.email = i['email']
						associate_person.phone_1 = i['phone_1']
						associate_person.phone_2 = i['phone_2']
						associate_person.supplier = supplier
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
		
		#print(result)
		return result

	@classmethod
	def get_data(cls, supplier):
		associate_person = []
		for a_s in cls.objects.filter(supplier=supplier):
			associate_person.append({
				"pk": a_s.pk,
				"name": a_s.name,
				"last_name": a_s.last_name,
				"email": a_s.email,
				"phone1": a_s.phone_1,
				"phone2": a_s.phone_2
			})
		return associate_person
	
	

class List_Price(models.Model):
	name = models.CharField(max_length = 50)
	percent = models.IntegerField()
	supplier = models.ForeignKey(Supplier, on_delete = models.CASCADE)

	def __str__(self):
		return f'{self.name} - {self.percent} by {self.supplier.name}'

	@classmethod
	def get_list_price(cls, supplier, data):
		try:
			price, created = cls.objects.get(supplier=supplier, name=data['name'])
		except cls.DoesNotExist:
			price = cls(name=data['name'], percent=data['percent'], supplier=supplier); price.save()
		return price

class Commercial_Information(models.Model):
	payment_deadline = models.CharField(max_length = 50)
	list_price = models.ForeignKey(List_Price, on_delete = models.CASCADE, related_name='supplier_list_price')
	cfdi = models.ForeignKey(CFDI, on_delete = models.CASCADE, related_name='supplier_cfdi')
	payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE, related_name='supplier_payment_method')
	payment_form = models.ForeignKey(Payment_Form, on_delete = models.CASCADE, related_name='supplier_payment_form')
	supplier = models.ForeignKey(Supplier, on_delete = models.CASCADE)

	@classmethod
	def create_commercial_information(cls, data, supplier):
		result = False
		message = None
		try:
			commercial_information = cls.objects.filter(pk=data["ci_pk"] if data["ci_pk"] != "" else 0).first()
			if not commercial_information:
				cp = cls(
					payment_deadline = data['payment_deadline'],
					list_price = List_Price.get_list_price(supplier, {"name":"test", "percent":0}),
					cfdi = CFDI.objects.get(pk = data['cfdi']),
					payment_method = Payment_Method.objects.get(pk = data['payment_method']),
					payment_form = Payment_Form.objects.get(pk = data['payment_form']),
					supplier = supplier
				)
				cp.save()
			else:
				commercial_information.payment_deadline = data['payment_deadline']
				#commercial_information.list_price = List_Price.get_list_price(customer, {"name":"test", "percent":0})
				commercial_information.cfdi = CFDI.objects.get(pk = data['cfdi'])
				commercial_information.payment_method = Payment_Method.objects.get(pk = data['payment_method'])
				commercial_information.payment_form = Payment_Form.objects.get(pk = data['payment_form'])
				commercial_information.supplier = supplier
				commercial_information.save()
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)

		return {'result':result, 'message':message}

	@classmethod
	def get_data(cls, supplier):
		commercial_information = {}
		for ci in cls.objects.filter(supplier=supplier):
			commercial_information = {
				"pk": ci.pk,
				"payment_deadline": ci.payment_deadline,
				"list_price": ci.list_price.pk,
				"list_price_name": ci.list_price.name,
				"cfdi": ci.cfdi.pk,
				"cfdi_name": ci.cfdi.name,
				"payment_method": ci.payment_method.pk,
				"payment_method_name": ci.payment_method.name,
				"payment_form": ci.payment_form.pk,
				"payment_form_name": ci.payment_form.name
			}
		return commercial_information

class Category(models.Model):
	name = models.CharField(max_length = 150, unique= True)

	def __str__(self):
		return self.name

	@classmethod
	def create_category(cls,data):
		category = cls(name = data['category'])
		category.save()
		for i in data['data']:
			if not create_subcategory(cls,i['name'],category.pk)['result']:
				break

	@classmethod
	def get_list_category(cls):
		return [
			{
				'pk_category':i.pk,
				'name': i.name
			}
			for i in cls.objects.all()
		]

class SubCategory(models.Model):
	name = models.CharField(max_length = 150, unique = True)
	category = models.ForeignKey(Category, on_delete = models.CASCADE)

	def __str__(self):
		return self.name

	@classmethod
	def create_subcategory(cls,name,pk):
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			cls(name = name,category=pk).save()
			result['code'] = 200
			result['status'] = 'OK'
			result['message'] = "Success"
		except IntegrityError as e:
			result['message'] = str(e)
		return result


	@classmethod
	def get_list_subcategory(cls, data):
		list_sub = []
		category = Category.objects.get(pk = data['pk_category'])
		for i in cls.objects.filter(category = category):
			serialized_subcategory = serializers.serialize('json', [i])
			subc = json.loads(serialized_subcategory)
			data = subc[0]['fields']
			data['pk_sub'] = subc[0]['pk']
			list_sub.append(data)
		return list_sub

class Product(models.Model):
	code = models.CharField(max_length = 30)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	quantity_unit = models.IntegerField(default=0, null = True, blank = True)
	bale_quantity = models.IntegerField(default=0, null = True, blank = True)
	price_1 = models.FloatField()
	price_2 = models.FloatField()
	price_3 = models.FloatField()
	tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True)
	unit_measure = models.ForeignKey(UnitMeasure, on_delete=models.SET_NULL, null=True)
	cost = models.FloatField()
	ipo = models.FloatField()
	discount = models.FloatField()
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	subcategory = models.ForeignKey(SubCategory, on_delete = models.CASCADE, null=True, blank=True)
	supplier = models.ForeignKey(Supplier, on_delete = models.CASCADE, null = True, blank = True)
	type_product = models.BooleanField(default=True)
	description = models.TextField()
	

	def __str__(self):
		return f"Product: {self.name} - Branch: {self.branch.name}"

	def calculate_profit_percentages(self):
		profit_percentages = {}
		prices = {
			'price': self.price,
			'price2': self.price2,
			'price3': self.price3
		}
		for price_field, price in prices.items():
			profit = (price - self.cost) * self.quantity
			profit_percentage = (profit / (self.cost * self.quantity)) * 100
			profit_percentages[price_field] = profit_percentage
		return profit_percentages

	@staticmethod
	def calculate_profit_amount(self):
		profit_amounts = {}
		prices = {
			'Price 1': self.price_1,
			'Price 2': self.price_2,
			'Price 3': self.price_3
		}
		
		for price_field, price in prices.items():
			try:
				profit_percentage = ((price - self.cost) / price) * 100
				profit_amount = (profit_percentage / 100) * price  # Calculate the amount of profit in money
				profit_amounts[price_field] = profit_amount
			except ZeroDivisionError as e:
				profit_amounts[price_field] = 0
		return profit_amounts

	def calculate_profit_percentages_one_quantity(self):
		profit_percentages = []
		prices = {
		    'Price 1': self.price_1,
		    'Price 2': self.price_2,
		    'Price 3': self.price_3
		}
		n = 1
		for price_field, price in prices.items():
			try:
				discounted_price = price - (price * (self.discount / 100))
				if discounted_price == self.cost:
					profit_percentage = 0  # If price equals cost after discount, profit percentage is 0
				else:
					profit_percentage = (((discounted_price - self.cost) / discounted_price) * 100)
				profit_percentages.append({
		            'percentage': f'{profit_percentage:.1f}%',
		            'name': price_field,
		            'id': n
		        })
			except ZeroDivisionError as e:
				profit_percentages.append({
		            'percentage': '0%',
		            'name': price_field,
		            'id': n
		        })
			n += 1

		return profit_percentages



	@staticmethod
	def Delete_Product_All(cls, branch):
		for i in cls.objects.filter(branch = branch):
			i.delete()

	@classmethod
	def create_product(cls,data):
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			employee = Employee.search_by_token(data['token'])
			branch = employee.branch

			if data['excel'] == 1:
				cls.Delete_Product_All(cls, branch)

			product = cls.objects.filter(branch = branch, code = data['code']).first()
			if product is None:
				try:
					print(data)
					product = cls(
						code = data['code'],
						name = data['name'],
						quantity = data['quantity'],
						tax = Tax.objects.filter(pk=data['tax']).first(),
						unit_measure = UnitMeasure.objects.filter(pk=data["unit_measure"]).first(),
						cost = data['cost'],
						price_1 = data['price_1'],
						price_2 = data['price_2'],
						price_3 = data['price_3'],
						ipo = data['ipo'],
						discount = data['discount'],
						branch = employee.branch,
						subcategory = SubCategory.objects.filter(pk = data['pk_subcategory']).first(),
						supplier = Supplier.objects.filter(pk = data['pk_supplier'], branch=branch).first(),
						type_product = True if data["type_product"] == "true" else False,
						description = data["description"]
					)
					product.save()
					branch = employee.branch
					message = "Success"
					serialized_employee = serializers.serialize('json', [employee])
					employee = json.loads(serialized_employee)
					History_Product.register_movement('Created', {}, data, employee ,branch)
					result['code'] = 200
					result['status'] = 'OK'
					result['message'] = "Success"
				except Exception as e:
					result['message'] = str(e)
			else:
				original_values = json.loads(serializers.serialize('json', [product]))[0]['fields']
				
				product.name = data['name']
				product.quantity = data['quantity']
				product.tax = Tax.objects.filter(pk=data['tax']).first()
				product.unit_measure = UnitMeasure.objects.filter(pk=data["unit_measure"]).first()
				product.cost = data['cost']
				product.price_1 = data['price_1']
				product.discount = data['discount']
				product.type_product = True if data["type_product"] == "true" else False
				product.description = data["description"]
				product.save()

				serialized_employee = serializers.serialize('json', [employee])
				employee = json.loads(serialized_employee)
				modified_values = {}
				for key, value in data.items():
					try:
						if int(original_values[key]) != value:
							modified_values[key] = original_values[key]
					except Exception as e:
						pass
				
				History_Product.register_movement('Modified', modified_values, data, employee, branch)

				result['code'] = 200
				result['status'] = 'OK'
				result['message'] = "Success"
		return result

	@classmethod
	def update_product(cls, data):
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			employee = Employee.search_by_token(data['token'])
			branch = employee.branch
			product = cls.objects.filter(branch=branch, code=data['code']).first()
			if product is not None:
				original_values = json.loads(serializers.serialize('json', [product]))[0]['fields']
				try:
					product.code = data['code']
					product.name = data['name']
					product.quantity = data['quantity']
					product.tax = data['tax']
					product.cost = data['cost']
					product.price_1 = data['price_1']
					product.price_2 = data['price_2']
					product.price_3 = data['price_3']
					product.ipo = data['ipo']
					product.discount = data['discount']
					product.branch = branch
					product.subcategory = SubCategory.objects.filter(pk=data['pk_subcategory']).first()
					product.supplier = Supplier.objects.filter(pk=data['pk_supplier']).first()
					product.type_product = True if data["type_product"] == "true" else False
					product.save()
					serialized_employee = serializers.serialize('json', [employee])
					employee = json.loads(serialized_employee)
					modified_values = {}
					for key, value in data.items():
						try:
							if int(original_values[key]) != value:
								modified_values[key] = original_values[key]
						except Exception as e:
							pass
					
					History_Product.register_movement('Modified', modified_values, data, employee, branch)
					result['code'] = 200
					result['status'] = 'OK'
					result['message'] = "Success"
				except Exception as e:
					result['message'] = str(e)
			else:
				result["message"] = "Product not exist"
		return result


	@classmethod
	def delete_product(cls,data):
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		employee = Employee.search_by_token(data['token'])
		branch = employee.branch
		try:
			_product = cls.objects.get(branch = branch, code = data['code'])
			serialized_employee = serializers.serialize('json', [employee])
			employee = json.loads(serialized_employee)
			serialized_product = serializers.serialize('json', [_product])
			product = json.loads(serialized_product)[0]['fields']
			History_Product.register_movement(action='Deleted', modified_values=product, product=product, employee=employee, branch=branch)
			_product.delete()
			result['code'] = 200
			result['status'] = 'OK'
			result['message'] = "Success"
		except cls.DoesNotExist as e:
			result['message'] = str(e)
		return result


	@classmethod
	def discount_product(cls,code, branch, quantity, employee):
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			pr = Product_Reserved.objects.get(user = employee, product= cls.objects.get(code = code))
			pr.delete()
			Best_Selling_Product.best_selling_product(code, branch, quantity)
			result['code'] = 200
			result['status'] = 'OK'
			result['message'] = "Success"
		except Exception as e:
			result['message'] = str(e)
		return result

	@classmethod
	def get_list_products(cls, data):
		result = {
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			branch = Employee.search_by_token(data['token']).branch
			for i in cls.objects.filter(branch = branch):
				product = serialized_employee = serializers.serialize('json', [i])
				result["data"].append(json.loads(product)[0]['fields'])
		return result

	@classmethod
	def get_list_products_supplier(cls, data):
		result = {
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			employee = Employee.search_by_token(data['token'])
			branch = employee.branch
			for i in cls.objects.filter(branch = branch, supplier = Supplier.objects.filter(pk = data['pk_supplier']).first()):
				product = serialized_employee = serializers.serialize('json', [i])
				result['data'].append(json.loads(product)[0]['fields'])
			result['code'] = 200
			result['status'] = 'OK'
			result['message'] = "Success"
		return result


	@classmethod
	def get_product(cls, data):
		employee = Employee.search_by_token(data['token'])
		branch = employee.branch
		_product = cls.objects.get(branch = branch, code = data['code'])
		product = serialized_employee = serializers.serialize('json', [_product])
		data = json.loads(product)[0]['fields']
		print(data)
		data['pk_cat'] = SubCategory.objects.filter(pk = data['subcategory']).first().category.pk if SubCategory.objects.filter(pk = data['subcategory']).first() else ""
		data['category'] = SubCategory.objects.filter(pk = data['subcategory']).first().category.name if SubCategory.objects.filter(pk = data['subcategory']).first() else ""
		data['pk_subcategory'] = SubCategory.objects.filter(pk = data['subcategory']).first().pk if SubCategory.objects.filter(pk = data['subcategory']).first() else ""
		data['subcategory'] = SubCategory.objects.filter(pk = data['subcategory']).first().name if SubCategory.objects.filter(pk = data['subcategory']).first() else ""
		data['pk_supplier'] = Supplier.objects.filter(pk = data['supplier']).first().pk if Supplier.objects.filter(pk = data['supplier']).first() else ""
		data['supplier'] = Supplier.objects.filter(pk = data['supplier']).first().name if Supplier.objects.filter(pk = data['supplier']).first() else ""
		data['calculate_profit_percentages'] = cls.calculate_profit_percentages_one_quantity(_product)
		data['calculate_profit_amount'] = cls.calculate_profit_amount(_product)
		data['pk_category'] = data['pk_cat']
		#result['list_subcategory'] = SubCategory.get_list_subcategory(data)
		data['pk_employee'] = employee.pk
		#result['list_supplier'] = Supplier.list_supplier(data)
		return data

class Best_Selling_Product(models.Model):
	product = models.ForeignKey(Product, on_delete = models.CASCADE)
	date = models.CharField(max_length = 15)
	sold = models.IntegerField()
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE, null = True, blank = True)

	@classmethod
	def best_selling_product(cls, code, branch, quantity):
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		product = Product.objects.get(code = code,branch = branch)
		try:
			bsp = cls.objects.get(product = product, date = _date.today())
			bsp.sold += quantity
			bsp.save()
			result['code'] = 200
			result['status'] = 'OK'
			result['message'] = "Success"
		except cls.DoesNotExist as e:
			bsp = cls(
				product = product,
				date = _date.today(),
				sold = quantity,
				branch = branch
			)
			bsp.save()
			result = True
			result['message'] = "Best Selling Product Created"
		return result

	


	@classmethod
	def get_best_selling_product(cls, data):
		result = False
		message = None
		quantity = 0
		try:
			product = Product.objects.get(code = data['code'],branch = data['pk_branch'])
			bsp = cls.objects.get(product = product, date = data['date'])
			result = True
			message = "Success"
			quantity = bsp.sold
		except Exception as e:
			message = str(e)
		return {'result': result, 'message':message,'quantity':quantity}

	@classmethod
	def get_list_best_selling_product(cls, data):
		result = False
		message = None
		_data = []
		total_sold = None
		try:
			branch = Branch.objects.get(pk=data['pk_branch'])
			start_date = data['start_date']
			end_date = data['end_date']
			queryset = cls.objects.filter(branch=branch)
			if start_date and end_date:
				queryset = queryset.filter(date__range=[start_date, end_date])
			top_selling_products = queryset.values('product__name').annotate(total_sold=Sum('sold')).order_by('-total_sold')[:10]
			total_sold = queryset.aggregate(Sum('sold'))['sold__sum']
			for i in queryset:
				serialized_data = json.loads(serializers.serialize('json', [i]))[0]
				serialized_data['fields']['product_code'] = i.product.code
				serialized_data['fields']['product_name'] = i.product.name
				serialized_data['fields']['total_sold'] = total_sold
				_data.append(serialized_data)
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result': result, 'message': message, 'data': _data}

	@classmethod
	def get_all_list_best_selling_product(cls, data):
		result = False
		message = None
		_data = []
		total_sold = None
		try:
			branch = Branch.objects.get(pk=data['pk_branch'])
			queryset = cls.objects.filter(branch=branch)
			top_selling_products = queryset.values('product__name').annotate(total_sold=Sum('sold')).order_by('-total_sold')
			for i in queryset:
				serialized_data = json.loads(serializers.serialize('json', [i]))[0]
				serialized_data['fields']['product_code'] = i.product.code
				serialized_data['fields']['product_name'] = i.product.name
				serialized_data['fields']['total_sold'] = total_sold
				_data.append(serialized_data)
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result': result, 'message': message, 'data': _data}


from datetime import date
class History_Product(models.Model):
	ACTION_CHOICES = (
	    ('Created', 'Created'),
	    ('Modified', 'Modified'),
	    ('Deleted', 'Deleted')
	)
	action = models.CharField(max_length=10, choices=ACTION_CHOICES)
	product = models.JSONField()
	employee = models.JSONField()
	timestamp = models.CharField(max_length = 15, null = True, blank = True)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE, null = True, blank = True)
	modified_values = models.JSONField(null = True, blank = True)

	def __str__(self):
		return f"{self.product.get('name', 'N/A')} - {self.action} by {self.employee[0]['fields']['user_name'].capitalize()} - {self.timestamp} "

	@classmethod
	def register_movement(cls, action, modified_values, product, employee, branch):
		history_product = cls(
			action = action,
			product = product,
			employee = employee,
			modified_values = modified_values,
			branch = branch,
			timestamp = date.today()
		)
		history_product.save()

from django.db import transaction
class Product_Reserved(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.IntegerField()
	user = models.ForeignKey(Employee, on_delete = models.CASCADE)

	@classmethod
	def reserveding_product(cls,data):
		user = Employee.search_by_token(data['token'])
		product = Product.objects.get(code = data['pk_product'],branch = user.branch)
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			pr = cls.objects.get(product = product, user = user)
			pr.quantity += int(data['quantity'])
			pr.save()
		except cls.DoesNotExist as e:
			result['message'] = str(e)
			pr = None
		if pr is None:
			pr = cls(product= product, quantity= int(data['quantity']),user = user)
			pr.save()
		if pr.quantity <= 0:
			pr.delete()
		if product.quantity >= int(data['quantity']):
			product.quantity -= int(data['quantity'])
			try:
				product.save()
				result['code'] = 200
				result['status'] = 'OK'
				result['message'] = "Success"
			except Exception as e:
				pass
		return result


	@classmethod
	def return_products(cls,pk_user):
		pr = cls.objects.filter(user = Employee.search_by_token(data['token']))
		for i in pr:
			p = Product.objects.get(pk = i.product.pk)
			p.quantity += i.quantity
			p.save()
			i.delete()
		return True

	@classmethod
	def return_product_unique(cls, data):
		user = Employee.search_by_token(data['token'])
		product = Product.objects.get(code=data['pk_product'], branch=user.branch)
		with transaction.atomic():
			_pr = cls.objects.get(product=product, user=user)
			number = int(str(data['quantity']).replace('-',''))
			if int(data['quantity']) < 0:
				_pr.quantity += 1
				_pr.save()
			else:
				_pr.quantity -= 1
				_pr.save()
			product.quantity += int(data['quantity'])
			product.save()
			if _pr.quantity <= 0:
				_pr.delete()
		return True
















