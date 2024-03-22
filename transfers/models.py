from django.db import models
from company.models import Branch, Resolution ,License, Consecutive
from inventory.models import Product, SubCategory, Supplier
from datetime import datetime
from django.core import serializers
from user.models import Employee
from django.http import JsonResponse
import json

class Transfer(models.Model):
	branch_sends = models.ForeignKey(Branch, on_delete= models.CASCADE, related_name="branch_sends")
	branch_receives = models.ForeignKey(Branch, on_delete= models.CASCADE, related_name="branch_receives")
	number = models.IntegerField(null=True, blank=True)
	note = models.TextField(null=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True,null=True, blank=True)
	returned = models.BooleanField(null=True, blank=True, default=False)
	timestamp_returned = models.CharField(max_length = 12, null = True, blank = True)

	@staticmethod
	def serializers_objects(obj):
		return json.loads(serializers.serialize('json', [obj]))[0]

	@classmethod
	def return_transfer(cls, data):
		result = False
		message = None
		try:
			transfer = cls.objects.get(pk = data['pk_transfer'], returned = False)
			details_transfer = Details_Transfer.objects.filter(transfer = transfer)
			_details_transfer = []
			for i in details_transfer:
				product = Product.objects.get(code = i.code, branch= transfer.branch_sends)
				_details_transfer.append(cls.serializers_objects(i))
				product.quantity += i.quantity
				i.quantity = 0
				i.price = 0
				i.ipo = 0
				i.discount = 0
				transfer.returned = True
				transfer.timestamp_returned = datetime.now()
				transfer.save()
				product.save()
				i.save()
			result = True
			message = "Success"
			_transfer = cls.serializers_objects(transfer)
			_transfer['details_transfer'] = _details_transfer
			branch_sends = cls.serializers_objects(transfer.branch_sends)
			employee = cls.serializers_objects(Employee.objects.get(pk = data['pk_employee']))
			return History_Transfer.create_history("Returned", branch_sends, employee, _transfer)
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

	@classmethod
	def transfer_products(cls, data):
		result = False
		message = None
		try:
			branch_sends = Branch.objects.get(pk = data['branch_sends'])
			consecutive = Consecutive.objects.get(branch= branch_sends)
			branch_receives = Branch.objects.get(pk = data['branch_receives'])
			transfer = cls(
				branch_sends = branch_sends,
				branch_receives = branch_receives,
				number = consecutive.tras,
				note = data['notes']
			)
			transfer.save()
			consecutive.tras += 1
			consecutive.save()
			if Details_Transfer.save_details(data, transfer):
				resolution = Resolution.objects.get(branch=branch_sends, type_document_id = 98)
				resolution._from += 1
				resolution.save()
				License.discount_license(branch_sends)
				message = "Success"
				result = True

			branch_sends = cls.serializers_objects(branch_sends)
			branch_receives = cls.serializers_objects(branch_receives)
			employee = cls.serializers_objects(Employee.objects.get(pk = data['pk_employee']))

			History_Transfer.create_history("Entrance", branch_receives, employee, data)
			History_Transfer.create_history("Exit", branch_sends, employee, data)
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}


class Details_Transfer(models.Model):
	code = models.CharField(max_length= 150)
	product = models.CharField(max_length = 250)
	quantity = models.IntegerField()
	price = models.IntegerField()
	ipo = models.IntegerField()
	discount = models.IntegerField()
	transfer = models.ForeignKey(Transfer, on_delete = models.CASCADE)

	@staticmethod
	def move_product(branch_sends, branch_receives, data):
		result =False
		_product = Product.objects.get(code=data['code'], branch=branch_sends)
		if _product.quantity > 0:
		    try:
		        product = Product.objects.get(code=data['code'], branch=branch_receives)
		        product.quantity += int(data['quantity'])
		        product.save()
		    except Product.DoesNotExist as e:
		        _data = json.loads(serializers.serialize('json', [_product]))[0]['fields']
		        _data.pop('id', None)
		        _data['branch'] = branch_receives
		        _data['subcategory'] = SubCategory.objects.get(pk = _data['subcategory'])
		        _data['supplier'] = Supplier.objects.filter(branch= branch_receives).first()
		        _data['quantity'] = data['quantity']
		        _data['price_1'] = data['price_1']
		        Product(**_data).save()
		    _product.quantity -= int(data['quantity'])
		    _product.save()
		    result = True
		return result

	@staticmethod
	def get_branch(pk):
		return Branch.objects.get(pk = pk)

	@classmethod
	def save_details(cls, data, transfer):
		result = False
		for i in data['details']:
			cls(
				code = i['code'],
				product = i['name'],
				quantity = i['quantity'],
				price = i['price_1'],
				ipo = i['ipo'],
				discount = i['discount'],
				transfer = transfer
			).save()
			result = True
			result = cls.move_product(cls.get_branch(data['branch_sends']), cls.get_branch(data['branch_receives']), i)
		return result


class History_Transfer(models.Model):
	ACTION_CHOICES = (
	    ('Entrance', 'Entrance'),
	    ('Exit', 'Exit'),
	    ('Returned', 'Returned'),
	)
	action = models.CharField(max_length=10, choices=ACTION_CHOICES)
	branch = models.JSONField()
	employee = models.JSONField()
	transfer = models.JSONField()
	timestamp = models.DateTimeField(auto_now_add=True)

	@classmethod
	def create_history(cls, action, branch, employee, transfer):
		result = False
		message = None
		try:
			history = cls(
				branch = branch,
				action = action,
				employee = employee,
				transfer = transfer
			)
			history.save()
			result = True
			message = "Success"
		except Exception as e:
			print(e)
			message = str(e)
		return {'result':result, 'message':message}

