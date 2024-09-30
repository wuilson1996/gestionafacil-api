from django.http import JsonResponse
from django.core import serializers
from django.db import IntegrityError
from company.models import Branch, Store
from django.db.models import Sum
from user.models import Employee
from django.db import models
from setting.models import *
from datetime import date as _date
import json
from django.conf import settings

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
				employee = Employee.search_by_token(token=data["token"])
				branch = employee.branch
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

					HistoryGeneral.create_history(
						action=HistoryGeneral.CREATED,
						class_models=HistoryGeneral.PROVIDER,
						class_models_json=json.loads(serializers.serialize('json', [supplier]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
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

					HistoryGeneral.create_history(
						action=HistoryGeneral.UPDATE,
						class_models=HistoryGeneral.PROVIDER,
						class_models_json=json.loads(serializers.serialize('json', [supplier]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
					
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
			employee = Employee.objects.filter(branch=branch).first()
			HistoryGeneral.create_history(
				action=HistoryGeneral.CREATED,
				class_models=HistoryGeneral.PROVIDER,
				class_models_json=json.loads(serializers.serialize('json', [supplier]))[0],
				employee=employee.pk,
				username=employee.user_django.username,
				branch=employee.branch.pk
			)
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
				employee = Employee.search_by_token(data['token'])
				branch = employee.branch
				_supplier = cls.objects.get(branch = branch, pk = data['pk_suppplier'])
				HistoryGeneral.create_history(
					action=HistoryGeneral.CREATED,
					class_models=HistoryGeneral.PROVIDER,
					class_models_json=json.loads(serializers.serialize('json', [_supplier]))[0],
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
				_supplier.delete()
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

class Commercial_Information(models.Model):
	payment_deadline = models.CharField(max_length = 50)
	list_price = models.ForeignKey(List_Price, on_delete = models.CASCADE, related_name='supplier_list_price', null=True, blank=True)
	seller_info = models.ForeignKey(SellerInfo, on_delete = models.CASCADE, related_name='supplier_seller', null=True, blank=True)
	term_payment = models.ForeignKey(TermPayment, on_delete = models.CASCADE, related_name='supplier_term_payment', null=True, blank=True)
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
				_term_payment = TermPayment.objects.filter(pk = data["pk_term_payment"]).first()
				cp = cls(
					payment_deadline = _term_payment.name if _term_payment else "",
					list_price = List_Price.objects.filter(pk = data["pk_list_price"]).first(),
					seller_info = SellerInfo.objects.filter(pk = data['pk_seller']).first(),
					term_payment = _term_payment,
					cfdi = CFDI.objects.get(pk = data['cfdi']),
					payment_method = Payment_Method.objects.get(pk = data['payment_method']),
					payment_form = Payment_Form.objects.get(pk = data['payment_form']),
					supplier = supplier
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

class Category(models.Model):
	name = models.CharField(max_length = 150)

	def __str__(self):
		return self.name

	@classmethod
	def create_category(cls,data):
		category = cls(name = data['category'])
		category.save()
		for i in data['data']:
			if not cls.create_subcategory(cls,i['name'],category.pk)['result']:
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
	name = models.CharField(max_length = 150)
	description = models.CharField(max_length=256)
	category = models.ForeignKey(Category, on_delete = models.CASCADE)
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE, blank=True, null=True)

	def __str__(self):
		return self.name

	@classmethod
	def create_subcategory(cls,name,pk):
		result = {
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
	def create_subcategory_by_branch(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(data['token'])
				_sub_category = cls.objects.filter(pk = data["pk"]).first()
				if not _sub_category:
					category = Category.objects.create(
						name = data["name"]
					)
					_sub_category = cls.objects.create(
						name = data["name"], 
						description=data["description"], 
						category=category, 
						branch=employee.branch
					)
					HistoryGeneral.create_history(
						action=HistoryGeneral.CREATED,
						class_models=HistoryGeneral.CATEGORY,
						class_models_json=json.loads(serializers.serialize('json', [_sub_category]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
				else:
					_category = _sub_category.category
					_category.name = data["name"]
					_category.save()

					_sub_category.name = data["name"]
					_sub_category.description = data["description"]
					_sub_category.save()

					HistoryGeneral.create_history(
						action=HistoryGeneral.UPDATE,
						class_models=HistoryGeneral.CATEGORY,
						class_models_json=json.loads(serializers.serialize('json', [_sub_category]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)

				result['code'] = 200
				result['status'] = 'OK'
				result['message'] = "Success"
		except IntegrityError as e:
			result['message'] = str(e)
			print(e)
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
	
	@classmethod
	def get_list_subcategory_by_branch(cls, data):
		result = {
			"data":[],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		if Employee.check_by_token(token=data["token"]):
			employee = Employee.search_by_token(data['token'])
			for c in cls.objects.filter(branch=employee.branch):
				_data1 = json.loads(serializers.serialize('json', [c]))[0]
				_data = _data1['fields']
				_data["pk"] = _data1["pk"]
				result["data"].append(_data)

			result['code'] = 200
			result['status'] = 'OK'
			result['message'] = "Success"
		return result
	
	@classmethod
	def delete_subcategory_by_branch(cls, data):
		result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(data['token'])
				_sub_category = cls.objects.filter(pk = data["pk"]).first()
				HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.CATEGORY,
					class_models_json=json.loads(serializers.serialize('json', [_sub_category]))[0],
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)

				_sub_category.category.delete()
				#_sub_category.delete()

				result['code'] = 200
				result['status'] = 'OK'
				result['message'] = "Success"
		except IntegrityError as e:
			result['message'] = str(e)
		return result
	
class Product(models.Model):
	code = models.CharField(max_length = 30)
	code_in = models.CharField(max_length = 50)
	name = models.CharField(max_length = 150)
	quantity = models.IntegerField()
	quantity_unit = models.IntegerField(default=0, null = True, blank = True)
	bale_quantity = models.IntegerField(default=0, null = True, blank = True)
	price_1 = models.FloatField()
	price_2 = models.FloatField()
	price_3 = models.FloatField()
	price_init = models.FloatField(default=0)
	tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True)
	unit_measure = models.ForeignKey(UnitMeasure, on_delete=models.SET_NULL, null=True)
	cost = models.FloatField()
	ipo = models.FloatField()
	discount = models.FloatField()
	branch = models.ForeignKey(Branch, on_delete = models.CASCADE)
	subcategory = models.ForeignKey(SubCategory, on_delete = models.CASCADE, null=True, blank=True)
	supplier = models.ForeignKey(Supplier, on_delete = models.CASCADE, null = True, blank = True)
	type_product = models.BooleanField(default=True)
	inventory = models.BooleanField(default=True)
	negative_sale = models.BooleanField(default=True)
	description = models.TextField()
	PS = "Producto o Servicio"
	GASTO = "Gasto"
	ACTIVO = "Activo"
	ITEM_TYPE = (
		(PS, "Producto o Servicio"),
		(GASTO, "Gasto"),
		(ACTIVO, "Activo"),
	)
	item_type = models.TextField(choices=ITEM_TYPE, default=PS)
	image = models.ImageField(upload_to="product", null=True, blank=True)
	image_b64 = models.TextField(null=True, blank=True)

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
	def save_file(cls, data):
		import base64
		import random
		_name_file = data["name_file"].split(".")[-2]
		_ext = data["name_file"].split(".")[-1]
		_name_file = _name_file+str(random.randint(100000, 999999))+"."+str(_ext)
		with open("media/product/"+_name_file, "wb") as file:
			file.write(base64.b64decode(bytes(data["file"], "utf-8") + b'=='))

		return _name_file

	@classmethod
	def clear_money(cls, price:str):
		return price.replace('$', "").replace(",", "")
	
	@classmethod
	def format_price(cls, price):
		price = str(price)
		clean_price = cls.clear_money(price)
		number = float(clean_price)
		formatted_price = "${:,.2f}".format(number)
		return formatted_price

	@classmethod
	def create_product(cls,data):
		result = {
			"data": {},
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				employee = Employee.search_by_token(data['token'])
				branch = employee.branch

				if data['excel'] == 1:
					cls.Delete_Product_All(cls, branch)

				#print(data)
				product = cls.objects.filter(branch = branch, pk = data['pk']).first()
				_file = ""
				if data["file"] != None:
					_file = cls.save_file(data)
				print(_file)
				if product is None:
					product = cls.objects.create(
						code = data['code'],
						code_in = data["code_in"],
						name = data['name'],
						quantity = data['quantity'],
						tax = Tax.objects.filter(pk=data['tax']).first(),
						unit_measure = UnitMeasure.objects.filter(pk=data["unit_measure"]).first(),
						cost = cls.clear_money(data['cost']),
						price_1 = cls.clear_money(data['price_1']),
						price_2 = data['price_2'],
						price_3 = data['price_3'],
						price_init = cls.clear_money(data["price_init"]),
						ipo = data['ipo'],
						discount = data['discount'],
						branch = employee.branch,
						subcategory = SubCategory.objects.filter(pk = data['pk_subcategory']).first(),
						supplier = Supplier.objects.filter(pk = data['pk_supplier'], branch=branch).first(),
						type_product = True if data["type_product"] == "true" else False,
						description = data["description"],
						#store = Store.objects.filter(pk = data["pk_store"]).first(),
						item_type = data["item_type"],
						inventory = data["inventoryProduct"],
						negative_sale = data["negativeSale"]
					)
					if _file != "":
						product.image = "product/"+_file
					if data["file"]:
						product.image_b64 = data["file"]
					product.save()
					branch = employee.branch

					for a in data["store"]:
						ProductInStore.product_in_store_create(a, product)

					for p in data["price_list"]:
						PriceByProduct.price_by_product_create(p, product)

					HistoryGeneral.create_history(
						action=HistoryGeneral.CREATED,
						class_models=HistoryGeneral.INVENTORY,
						class_models_json=json.loads(serializers.serialize('json', [product]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
				else:
					original_values = json.loads(serializers.serialize('json', [product]))[0]['fields']
					
					product.code = data["code"]
					product.code_in = data["code_in"]
					product.name = data['name']
					product.quantity = data['quantity']
					product.tax = Tax.objects.filter(pk=data['tax']).first()
					product.unit_measure = UnitMeasure.objects.filter(pk=data["unit_measure"]).first()
					product.price_init = cls.clear_money(data["price_init"])
					product.cost = cls.clear_money(data['cost'])
					product.price_1 = cls.clear_money(data['price_1'])
					product.discount = data['discount']
					product.type_product = True if data["type_product"] == "true" else False
					product.description = data["description"]
					#product.store = Store.objects.filter(pk = data["pk_store"]).first()
					product.item_type = data["item_type"]
					product.inventory = data["inventoryProduct"]
					product.negative_sale = data["negativeSale"]
					if _file != "":
						product.image = "product/"+_file
					if data["file"]:
						product.image_b64 = data["file"]
					product.save()

					modified_values = {}
					for key, value in data.items():
						try:
							if int(original_values[key]) != value:
								modified_values[key] = original_values[key]
						except Exception as e:
							pass
					
					# validacion de objects borrados y nuevos.
					for pins in ProductInStore.objects.filter(product=product):
						state_delete = True
						for a in data["store"]:
							if int(pins.pk) == int(a["pk"]):
								state_delete = False
								break
						if state_delete:
							pins.delete()

					for a in data["store"]:
						ProductInStore.product_in_store_create(a, product)

					for pbys in PriceByProduct.objects.filter(product=product):
						state_delete = True
						for a in data["price_list"]:
							if int(pbys.pk) == int(a["pk"]):
								state_delete = False
								break
						if state_delete:
							pbys.delete()

					for p in data["price_list"]:
						PriceByProduct.price_by_product_create(p, product)

					HistoryGeneral.create_history(
						action=HistoryGeneral.UPDATE,
						class_models=HistoryGeneral.INVENTORY,
						class_models_json=json.loads(serializers.serialize('json', [product]))[0],
						employee=employee.pk,
						username=employee.user_django.username,
						branch=employee.branch.pk
					)
				result['code'] = 200
				result['status'] = 'OK'
				result['message'] = "Success"
				result["data"]["pk"] = product.pk
		except Exception as err:
			result['message'] = str(err)
			print(err)
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
			_product = cls.objects.get(branch = branch, pk = data['pk'])
			#serialized_employee = serializers.serialize('json', [employee])
			#employee = json.loads(serialized_employee)
			serialized_product = serializers.serialize('json', [_product])
			product = json.loads(serialized_product)[0]
			HistoryGeneral.create_history(
				action=HistoryGeneral.DELETE,
				class_models=HistoryGeneral.INVENTORY,
				class_models_json=product,
				employee=employee.pk,
				username=employee.user_django.username,
				branch=employee.branch.pk
			)
			#History_Product.register_movement(action='Deleted', modified_values=product, product=product, employee=employee, branch=branch)
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
			for i in cls.objects.filter(branch = branch).order_by("-id"):
				if i.item_type in data["item_type"]:
					product = serialized_employee = serializers.serialize('json', [i])
					_product_data = json.loads(product)[0]['fields']
					_product_data["pk"] = i.pk
					_product_data["price_1_money"] = cls.format_price(float(i.price_1))
					_product_data["cost_money"] = cls.format_price(float(i.cost))
					#_store = Store.objects.filter(pk = _product_data["store"]).first()
					#_product_data["store_name"] = _store.name if _store else ""
					_product_data["store_list"] = []
					_product_data["store"] = []
					for sl in ProductInStore.objects.filter(product=i):
						aux_store_list = json.loads(serializers.serialize('json', [sl]))[0]['fields']
						aux_store_list["pk"] = sl.pk
						_product_data["store_list"].append(aux_store_list)
						_product_data["store"].append(sl.store.pk)

					_product_data["price_list"] = []
					for pbp in PriceByProduct.objects.filter(product=i):
						aux_price_list = json.loads(serializers.serialize('json', [pbp]))[0]['fields']
						aux_price_list["pk"] = pbp.pk
						_product_data["price_list"].append(aux_price_list)
					result["data"].append(_product_data)

			result['code'] = 200
			result['status'] = 'OK'
			result['message'] = "Success"
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
				result["data"]["pk"] = i.pk
			result['code'] = 200
			result['status'] = 'OK'
			result['message'] = "Success"
		return result


	@classmethod
	def get_product(cls, data):
		employee = Employee.search_by_token(data['token'])
		branch = employee.branch
		_product = cls.objects.get(branch = branch, pk = data['pk'])
		product = serializers.serialize('json', [_product])
		data = json.loads(product)[0]['fields']
		data["pk"] = _product.pk
		#print(data)
		data['pk_cat'] = SubCategory.objects.filter(pk = data['subcategory']).first().category.pk if SubCategory.objects.filter(pk = data['subcategory']).first() else ""
		data['category'] = SubCategory.objects.filter(pk = data['subcategory']).first().category.name if SubCategory.objects.filter(pk = data['subcategory']).first() else ""
		data['pk_subcategory'] = SubCategory.objects.filter(pk = data['subcategory']).first().pk if SubCategory.objects.filter(pk = data['subcategory']).first() else ""
		data['subcategory'] = SubCategory.objects.filter(pk = data['subcategory']).first().name if SubCategory.objects.filter(pk = data['subcategory']).first() else ""
		data['pk_supplier'] = Supplier.objects.filter(pk = data['supplier']).first().pk if Supplier.objects.filter(pk = data['supplier']).first() else ""
		data['supplier'] = Supplier.objects.filter(pk = data['supplier']).first().name if Supplier.objects.filter(pk = data['supplier']).first() else ""
		data['calculate_profit_percentages'] = cls.calculate_profit_percentages_one_quantity(_product)
		data['calculate_profit_amount'] = cls.calculate_profit_amount(_product)
		data["image"] = settings.URL_API+"/media/"+data["image"]

		data["store_list"] = []
		for sl in ProductInStore.objects.filter(product=_product):
			aux_store_list = json.loads(serializers.serialize('json', [sl]))[0]['fields']
			aux_store_list["pk"] = sl.pk
			data["store_list"].append(aux_store_list)

		data["price_list"] = []
		for pbp in PriceByProduct.objects.filter(product=_product):
			aux_price_list = json.loads(serializers.serialize('json', [pbp]))[0]['fields']
			aux_price_list["pk"] = pbp.pk
			data["price_list"].append(aux_price_list)

		data['pk_category'] = data['pk_cat']
		#result['list_subcategory'] = SubCategory.get_list_subcategory(data)
		data['pk_employee'] = employee.pk
		#result['list_supplier'] = Supplier.list_supplier(data)
		return data

class ProductInStore(models.Model):
	product = models.ForeignKey(Product, on_delete = models.CASCADE)
	store = models.ForeignKey(Store, on_delete = models.CASCADE, null = True, blank = True)
	cant_init = models.FloatField(default=0)
	cant_min = models.FloatField(default=0)
	cant_max = models.FloatField(default=0)

	def __str__(self) -> str:
		return str(self.product)

	@classmethod
	def product_in_store_create(cls, data, product:Product):
		_product_in_store = cls.objects.filter(pk = data["pk"]).first()
		if not _product_in_store:
			_product_in_store = cls.objects.create(
				product = product,
				store = Store.objects.filter(pk = data["store"]).first(),
				cant_init = data["cant_init"],
				cant_min = data["cant_min"],
				cant_max = data["cant_max"]
			)
		else:
			_product_in_store.store = Store.objects.filter(pk = data["store"]).first()
			_product_in_store.cant_init = data["cant_init"]
			_product_in_store.cant_min = data["cant_min"]
			_product_in_store.cant_max = data["cant_max"]
			_product_in_store.save()

class PriceByProduct(models.Model):
	product = models.ForeignKey(Product, on_delete = models.CASCADE)
	list_price = models.ForeignKey(List_Price, on_delete = models.CASCADE)
	valor = models.FloatField(default=0)

	def __str__(self) -> str:
		return str(self.product)
	
	@classmethod
	def price_by_product_create(cls, data, product:Product):
		_product_in_store = cls.objects.filter(pk = data["pk"]).first()
		if not _product_in_store:
			_product_in_store = cls.objects.create(
				product = product,
				list_price = List_Price.objects.filter(pk = data["price"]).first(),
				valor = data["valor"]
			)
		else:
			_product_in_store.list_price = List_Price.objects.filter(pk = data["price"]).first()
			_product_in_store.valor = data["valor"]
			_product_in_store.save()

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
















