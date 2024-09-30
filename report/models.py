from inventory.models import Product, History_Product
from django.core import serializers
from invoice.models import Invoice, Details_Invoice, Payment_Forms, PaymentToPayInvoice
from user.models import Employee
from shopping.models import Shopping
from django.db.models import Sum
from django.db.models import Q
from datetime import datetime
from django.db import models
import json

def parse_date(_date:str):
	return datetime(year=int(_date.split("-")[0]), month=int(_date.split("-")[1]), day=int(_date.split("-")[2]))

class Report_Invoice(models.Model):

	@classmethod
	def list_invoice_by_item(cls, data):
		result = {
			"totals":{
				"total_by_tax": 0,
				"total": 0,
			},
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				products = {}
				for i in Invoice.objects.filter(branch = branch, type_document = data['type_document']).order_by('-pk'):
					_date = parse_date(i.date)
					_date_from = parse_date(str(data["date_from"]))
					_date_to = parse_date(str(data["date_to"]))
					if _date >= _date_from and _date <= _date_to:
						detail = Details_Invoice.objects.filter(invoice=i)
						for d in detail:
							#print(d.code)
							if d.product:
								if d.product.pk not in list(products.keys()):
									products[d.product.pk] = {
										"name": d.name,
										"code": d.code,
										"cant": 0,
										"total": 0,
										"total_by_tax": 0
									}

								products[d.product.pk]["cant"] += d.quantity
								products[d.product.pk]["total"] += d.price * d.quantity
								products[d.product.pk]["total_by_tax"] += d.cost * d.quantity
								result["totals"]["total"] += d.price * d.quantity
								result["totals"]["total_by_tax"] += d.cost * d.quantity

				result["data"] = list(products.values())
				result['code'] = 200
				result["message"] = "Success"
				result["status"] = "OK"
		except Exception as e:
			result['message'] = str(e)
	
		return result
	
	@classmethod
	def list_invoice_by_client(cls, data):
		result = {
			"totals":{
				"total_by_tax": 0,
				"total": 0,
			},
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				clients = {}
				for i in Invoice.objects.filter(branch = branch, type_document = data['type_document']).order_by('-pk'):
					_date = parse_date(i.date)
					_date_from = parse_date(str(data["date_from"]))
					_date_to = parse_date(str(data["date_to"]))
					if _date >= _date_from and _date <= _date_to:
						if i.customer.identification_number not in list(clients.keys()):
							clients[i.customer.identification_number] = {
								"name": i.customer.name,
								"document": i.customer.identification_number,
								"cant_document": 0,
								"total": 0,
								"total_by_tax": 0
							}
						
						clients[i.customer.identification_number]["cant_document"] += 1
						detail = Details_Invoice.objects.filter(invoice=i)
						for d in detail:
							clients[i.customer.identification_number]["total"] += d.price * d.quantity
							clients[i.customer.identification_number]["total_by_tax"] += d.cost * d.quantity
							result["totals"]["total"] += d.price * d.quantity
							result["totals"]["total_by_tax"] += d.cost * d.quantity

						clients[i.customer.identification_number]

				result["data"] = list(clients.values())
				result['code'] = 200
				result["message"] = "Success"
				result["status"] = "OK"
		except Exception as e:
			result['message'] = str(e)
	
		return result

	@classmethod
	def list_invoice_by_seller(cls, data):
		result = {
			"totals":{
				"total_by_tax": 0,
				"total": 0,
			},
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				sellers = {}
				from customer.models import Commercial_Information
				for i in Invoice.objects.filter(branch = branch, type_document = data['type_document']).order_by('-pk'):
					_date = parse_date(i.date)
					_date_from = parse_date(str(data["date_from"]))
					_date_to = parse_date(str(data["date_to"]))
					if _date >= _date_from and _date <= _date_to:
						ci = Commercial_Information.objects.filter(customer=i.customer).first()
						if ci:
							if ci.seller_info.pk not in list(sellers.keys()):
								sellers[ci.seller_info.pk] = {
									"seller_pk": ci.seller_info.pk,
									"name": ci.seller_info.name,
									"cant_document": 0,
									"total": 0,
									"total_by_tax": 0
								}
							sellers[ci.seller_info.pk]["cant_document"] += 1
							detail = Details_Invoice.objects.filter(invoice=i)
							for d in detail:
								sellers[ci.seller_info.pk]["total"] += d.price * d.quantity
								sellers[ci.seller_info.pk]["total_by_tax"] += d.cost * d.quantity
								result["totals"]["total"] += d.price * d.quantity
								result["totals"]["total_by_tax"] += d.cost * d.quantity

				result["data"] = list(sellers.values())
				result['code'] = 200
				result["message"] = "Success"
				result["status"] = "OK"
		except Exception as e:
			result['message'] = str(e)
		return result
	
	@classmethod
	def list_invoice_by_account(cls, data):
		result = {
			"totals":{
				"total": 0,
				"retention": 0,
				"cobrado": 0,
				"saldo": 0
			},
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				from customer.models import Customer
				for i in Invoice.objects.filter(branch = branch, customer=Customer.objects.filter(pk = data["pk_customer"]).first()).order_by('-pk'):
					_date = parse_date(i.date)
					_date_from = parse_date(str(data["date_from"]))
					_date_to = parse_date(str(data["date_to"]))
					if _date >= _date_from and _date <= _date_to:
						state_account = PaymentToPayInvoice.objects.filter(invoice=i).last()
						result["totals"]["total"] += i.total
						result["totals"]["cobrado"] += state_account.amount
						result["totals"]["saldo"] += i.total - state_account.amount
						result["data"].append(
							{
								"type_document":i.type_document,
								'pk_invoice': i.pk,
								'number': i.number,
								'prefix': i.prefix,
								'date': i.date,
								'name_client': i.customer.name,
								'pk_client': i.customer.pk,
								'total': i.total if i.total else 0,
								"state": i.state_invoice,
								"cancelled":i.cancelled,
								"expiration": str(state_account.date.date()),
								"days": (datetime.now().date() - state_account.date.date()).days,
								"cobrado": state_account.amount,
								"pending": i.total - state_account.amount,
								"retention": 0
							}
						)
				result['code'] = 200
				result["message"] = "Success"
				result["status"] = "OK"
		except Exception as e:
			result['message'] = str(e)
			print(e)
		return result

	@classmethod
	def list_invoice_by_item_profit(cls, data):
		result = {
			"totals":{
				"cost": 0,
				"total": 0,
				"rentable": 0
			},
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				products = {}
				for i in Invoice.objects.filter(branch = branch, type_document = data['type_document']).order_by('-pk'):
					_date = parse_date(i.date)
					_date_from = parse_date(str(data["date_from"]))
					_date_to = parse_date(str(data["date_to"]))
					if _date >= _date_from and _date <= _date_to:
						detail = Details_Invoice.objects.filter(invoice=i)
						for d in detail:
							#print(d.code)
							if d.product:
								if d.product.pk not in list(products.keys()):
									products[d.product.pk] = {
										"name": d.name,
										"code": d.code,
										"cant": 0,
										"total": 0,
										"cost": 0,
										"rentable": 0,
										"porcent": 0
									}

								products[d.product.pk]["cant"] += d.quantity
								products[d.product.pk]["total"] += d.cost * d.quantity
								products[d.product.pk]["cost"] += d.product.price_init * d.quantity
								products[d.product.pk]["rentable"] += (d.cost * d.quantity) - (d.product.price_init * d.quantity)

								result["totals"]["total"] += d.cost * d.quantity
								result["totals"]["cost"] += d.product.price_init * d.quantity
								result["totals"]["rentable"] += (d.cost * d.quantity) - (d.product.price_init * d.quantity)

				for _, value in products.items():
					value['porcent'] = (float(value['rentable']) / float(value['total'])) * 100
				result["data"] = list(products.values())
				result['code'] = 200
				result["message"] = "Success"
				result["status"] = "OK"
		except Exception as e:
			result['message'] = str(e)
			print(e)

		return result

	@classmethod
	def list_invoice(cls, data):
		chart = {}
		for y in data['year']:
			chart[y] = {
				"jan": 0,
				"feb": 0,
				"mar": 0,
				"apr": 0,
				"may": 0,
				"jun": 0,
				"jul": 0,
				"aug": 0,
				"sep": 0,
				"oct": 0,
				"nov": 0,
				"dec": 0
			}
		month_text_num = {
			"01": "jan",
			"02": "feb",
			"03": "mar",
			"04": "apr",
			"05": "may",
			"06": "jun",
			"07": "jul",
			"08": "aug",
			"09": "sep",
			"10": "oct",
			"11": "nov",
			"12": "dec"
		}
		result = {
			"year":data["year"],
			"chart": [],
			"totals":{
				"subtotal": 0,
				"discount": 0,
				"sales": 0,
				"credit_note": 0,
				"tax": 0,
				"total_by_tax": 0,
				"total": 0
			},
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
		try:
			if Employee.check_by_token(token=data["token"]):
				branch = Employee.search_by_token(data['token']).branch
				from inventory.models import ProductInStore
				from company.models import SerieFolio
				for i in Invoice.objects.filter(branch = branch, type_document = data['type_document']).order_by('-pk'):
					
					# add filter to chart anios
					#if i.date.split("-")[0] in data['year']:
					#	chart[i.date.split("-")[0]][month_text_num[i.date.split("-")[1]]] += i.total if i.total else 0

					# add filter dates.
					_date = parse_date(i.date)
					_date_from = parse_date(str(data["date_from"]))
					_date_to = parse_date(str(data["date_to"]))

					#print(_date_from, _date_to)
					# check number.
					_num = False
					if data["num"]:
						for n in data["num"]:
							_serie_folio = SerieFolio.objects.filter(pk = n).first()
							if _serie_folio.serie == i.prefix:
								_num = True
								break
					else:
						_num = True
					
					if _date >= _date_from and _date <= _date_to and _num:
						detail = Details_Invoice.objects.filter(invoice=i)
						discount = 0
						tax = 0
						subtotal = 0
						_store = False
						for d in detail:
							tax += d.tax * d.quantity
							discount += d.discount * d.quantity
							subtotal += d.cost * d.quantity
							if data["store"]:
								# check store product
								product_in_store = ProductInStore.objects.filter(product=d.product)
								for pis in product_in_store:
									if pis.store.pk in data["store"]:
										_store = True
										break
							else:
								_store = True

						if _store:
							chart[i.date.split("-")[0]][month_text_num[i.date.split("-")[1]]] += i.total if i.total else 0
							result['totals']["subtotal"] += subtotal
							result['totals']["discount"] += discount
							result['totals']["sales"] += i.total if i.total else 0
							result['totals']["tax"] += tax
							result['totals']["total_by_tax"] += subtotal
							result['totals']["total"] += subtotal + tax

							state_account = PaymentToPayInvoice.objects.filter(invoice=i).last()

							result["data"].append(
								{
									"type_document":i.type_document,
									'pk_invoice': i.pk,
									'number': i.number,
									'prefix': i.prefix,
									'date': i.date,
									'name_client': i.customer.name,
									'pk_client': i.customer.pk,
									'total': i.total if i.total else 0,
									"state_invoice":i.state,
									"state": i.state_invoice,
									"tax":tax,
									"discount":discount,
									"subtotal":subtotal,
									"cancelled":i.cancelled
								}
							)

				result["totals"]["sales"] -= result['totals']["discount"]
				#print(list(chart.values()))
				for key, value in chart.items():
					result['chart'].append({key: value})
				result['code'] = 200
				result["message"] = "Success"
				result["status"] = "OK"
		except Exception as e:
			result['message'] = str(e)
			print(e)
		return result
	
	@staticmethod
	def return_value_tax(tax,obj):
		value = 0
		if obj.tax_value == tax:
			value = obj.tax
		return round(value)

	@staticmethod
	def return_value_base(tax,obj):
		value = 0
		if obj.tax_value == tax:
			value = obj.price * obj.quantity
		return round(value)

	@staticmethod
	def return_value_ipo(tax,obj):
		value = 0
		if obj.tax_value == tax:
			value = obj.ipo * obj.quantity
		return round(value)

	
	@classmethod
	def close_the_box_all(cls, data):
		_data = []
		efec = 0; trans = 0; cred = 0; tax_0 = 0; tax_5 = 0; tax_19 = 0; base_0 = 0; base_5 = 0; base_19 = 0; ipo_0 = 0; ipo_5 = 0; ipo_19 = 0; total = 0; efec_pos = 0; efec_elect = 0;
		for invoice in Invoice.objects.filter(branch = Employee.objects.get(pk = data['pk_employee']).branch, date__range= (data['date_start'], data['date_end'])):
			di = Details_Invoice.objects.filter(invoice = invoice)
			pf = Payment_Forms.objects.get(invoice = invoice)
			for i in di:
				tax_0 += cls.return_value_tax(0,i)
				tax_5 += cls.return_value_tax(5,i)
				tax_19 += cls.return_value_tax(19,i)

				base_0 += cls.return_value_base(0,i)
				base_5 += cls.return_value_base(5,i)
				base_19 += cls.return_value_base(19,i)

				ipo_0 += cls.return_value_ipo(0,i)
				ipo_5 += cls.return_value_ipo(5,i)
				ipo_19 += cls.return_value_ipo(19,i)

			efec_pos += int(invoice.total) if pf.payment_method._id == 10 else 0
			efec_elect += int(invoice.total) if pf.payment_method._id == 10 and invoice.type_document == 2 else 0
			efec += int(invoice.total) if pf.payment_method._id == 10 else 0
			cred += invoice.total if pf.payment_method._id == 30 else 0
			trans += invoice.total if pf.payment_method._id == 35 else 0
			total += invoice.total

		_data.append({
			'tax_0':tax_0,
			'tax_5':tax_5,
			'tax_19':tax_19,
			'efe':efec,
			'efec_pos':efec_pos,
			'efec_elect':efec_elect,
			'cred':cred,
			'trans':trans,
			'base_0':base_0,
			'base_5':base_5,
			'base_19':base_19,
			'ipo_0':ipo_0,
			'ipo_5':ipo_5,
			'ipo_19':ipo_19,
			'total_pf': efec + cred + trans,
			'total_base': base_0 + base_5 + base_19,
			'total_tax': tax_0 + tax_5 + tax_19,
			'total_ipo': ipo_0 + ipo_5 + ipo_19,
			"totals": total
		})
		return _data



	@classmethod
	def list_invoice_annulled(cls, data):
		return [
				{
					"type_document":i.type_document,
					'pk_invoice': i.pk,
					'number': i.number,
					'prefix': i.prefix,
					'date': i.date,
					'name_client': i.customer.name,
					'total': i.total,
					"state":i.state,
					"cancelled":i.cancelled
				}
				for i in Invoice.objects.filter(branch = Employee.objects.get(pk = data['pk_employee']).branch, annulled = True, type_document = data['type_document']).order_by('-pk')
			]
	@staticmethod
	def serializers_data(obj):
		serialized_customer = serializers.serialize('json', [obj])
		return json.loads(serialized_customer)[0]

	@classmethod
	def close_the_box(cls, data):
		result = False
		message = None
		_data = {}
		try:
			invoice = Invoice.objects.filter(branch = Employee.objects.get(pk = data['pk_employee']).branch, type_document = data['type_document'], date__range =(data['date_start'], data['date_end']))
			for i in invoice:
				_data = cls.serializers_data(i)
				tax = sum(di.tax * di.quantity for di in Details_Invoice.objects.filter(invoice=i))
				price = sum(di.price * di.quantity for di in Details_Invoice.objects.filter(invoice=i))
				_data['fields']['tax_totals']
				_data['fields']['price_totals']
		except Exception as e:
			raise e
		return 



class Report_Inventory(models.Model):

	@classmethod
	def list_product(cls ,data):
		product = Product.objects.filter(branch = Employee.objects.get(pk = data['pk_employee']).branch)
		data = []
		for i in product:
			value = json.loads(serializers.serialize('json', [i]))[0]
			value['product_name'] = i.name
			data.append(value)
		return data

	@classmethod
	def report_product(cls, data):
		return True
		# branch = Employee.objects.get(pk = data['pk_employee']).branch
		# invoice = Invoice.objects.filter(branch = branch)
		# for i in invoice:
		# 	di = Details_Invoice.objects.filter()
		# 	product = Product.objects.get(code = data['code'])
		return json.loads(serializers.serialize('json', [product]))[0]
	

class Report_Shopping(models.Model):

	@classmethod
	def get_invoice_shopping(cls, data):
		shopping = Shopping.objects.filter(branch=Employee.objects.get(pk=data['pk_employee']).branch, annulled=False)
		return [
				{
					'pk_invoice': i.pk,
					'number': i.number,
					'date': i.date,
					'name_supplier': i.supplier.name,
					'total': i.total,
					"cancelled":i.cancelled
				}
				for i in shopping
			]




class Hitory(models.Model):

	@classmethod
	def history_inventory(cls, data):
		result = False
		message = None
		_data = []
		try:
			hi = History_Product.objects.filter(Q(timestamp__range = (data['date_start'], data['date_end'])), branch = Employee.objects.get(pk = data['pk_employee']).branch )
			for i in hi:
				product = serialized_employee = serializers.serialize('json', [i])
				_data.append(json.loads(product)[0]['fields'])
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result': result, 'message':message, 'data':_data}
