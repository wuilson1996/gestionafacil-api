from inventory.models import Product, History_Product
from django.core import serializers
from invoice.models import Invoice, Details_Invoice, Payment_Forms
from user.models import Employee
from shopping.models import Shopping
from django.db.models import Sum
from django.db.models import Q
from datetime import datetime
from django.db import models
import json

class Report_Invoice(models.Model):

	@classmethod
	def list_invoice(cls, data):
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
				for i in Invoice.objects.filter(branch = Employee.objects.get(pk = data['pk_employee']).branch, type_document = data['type_document']).order_by('-pk')
			]

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
