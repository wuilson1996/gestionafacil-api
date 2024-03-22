from datetime import datetime, timedelta, date as _date
from from_number_to_letters import Thousands_Separator
from django.core import serializers
from company.models import Resolution
import json, requests, numpy as np
from user.models import Employee, Payment_Form_Employee
from django.db import models
from decimal import Decimal
from invoice.models import Invoice
from setting.models import *


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, Decimal):
        	return float(obj)
        return super(NpEncoder, self).default(obj)

class Payroll(models.Model):
	data_payroll = models.JSONField(null = True, blank= True)
	employee = models.ForeignKey(Employee, on_delete= models.CASCADE, null = True, blank= True)
	cune = models.CharField(max_length = 70, null = True, blank= True)
	annulled = models.BooleanField(default= False)
	was_sent = models.BooleanField(default= False)

	def __str__(self):
		return f"{self.data_payroll.get('consecutive', 'N/A')}"#" - {self.employee.first_name} {self.employee.surname} by {self.employee.branch.name}"

	@classmethod
	def get_all_payroll_employee(cls, data):
		employee = Employee.objects.get(pk = data['pk_employee'])
		value = json.loads(serializers.serialize('json', [employee]))[0]
		_data = value['fields']
		_data['pk_employee'] = value['pk']
		_data['municipality_name'] = Municipalities.objects.get(pk = _data['municipality_id']).name
		_data['total_selling'] = sum(i.total for i in Invoice.objects.filter(employee = employee))
		_data['payroll'] = [ json.loads(serializers.serialize('json', [i]))[0]['fields'] for i in cls.objects.filter(employee = employee).order_by('-pk') ]
		for i in _data['payroll']:
			i['data_payroll']['total_payroll'] = Thousands_Separator(float(i['data_payroll']['accrued']['accrued_total']) - float(i['data_payroll']['deductions']['deductions_total']))
		return _data

	@classmethod
	def create_data_payroll(cls, data):
		result = False
		message = None
		print(type(data))
		try:
			payroll = cls(data_payroll = data)
			payroll.save()
			result = True
			message = True
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message}

	@classmethod
	def get_list_payroll(cls, data):
		result = False
		message = None
		_data = []
		try:
			_data = [ i.data_payroll for i in cls.objects.filter(employee=Employee.objects.get(pk = data['pk_employee']))]
			result = True
			message = "Success"
		except cls.DoesNotExist as e:
			message = str(e)
		return {'result':result, 'message':message, 'data': _data}


	@staticmethod
	def payroll_periods(worked_days):
		return { '7':1, '10':2, '14':3, '15':4, '30':5 }[ str( worked_days ) ]


	@classmethod
	def basic_payroll(cls, data):
		date_string = datetime.now().strftime('%Y-%m-%d')
		date = datetime.strptime(date_string, '%Y-%m-%d')
		one_month_ago = date - timedelta(days=date.day)
		month = one_month_ago.strftime('%m')
		year = one_month_ago.year
		settlement_start_date = f"{year}-{month}-01"
		settlement_end_date = (one_month_ago + timedelta(days=30)).strftime('%Y-%m-%d')
		worked_time = 780
		issue_date = date_string
		employee = Employee.objects.get(pk = data['pk_employee'])
		worked_days = int(data['worked_days'])
		value_days = (employee.salary / 30)

		salary = float(value_days * worked_days)
		transportation_allowance = float((115000 / 30) * worked_days)
		accrued_total = salary + transportation_allowance

		eps_deduction = float(salary * 0.4)
		pension_deduction = float(salary * 0.4)
		deductions_total = eps_deduction + pension_deduction
		payment_form_employee = Payment_Form_Employee.objects.get(employee= employee)

		type_document = 9
		payroll = {
		    "type_document_id": type_document,
		    "establishment_name": employee.branch.name,
		    "establishment_address": employee.branch.address,
		    "establishment_phone": employee.branch.phone,
		    "establishment_municipality": employee.branch.municipality._id,
		    "head_note": "",
		    "foot_note": "",
		    "novelty": {
		        "novelty": False,
		        "uuidnov": ""
		    },
		    "payment_dates": [
		        {
		            "payment_date": str(_date.today())
		        }
		    ],
		    "period": {
		        "admision_date": str(_date.today()),
		        "settlement_start_date": settlement_start_date,
		        "settlement_end_date": (one_month_ago + timedelta(days=30)).strftime('%Y-%m-%d'),
		        "worked_time": f"{data['worked_time']}",
		        "issue_date": str(_date.today())
		    },
		    "sendmail": False,
		    "sendmailtome": False,
		    "worker_code": "1",
		    "prefix": "NI",
		    "consecutive": Resolution.get_number(type_document),
		    "payroll_period_id": cls.payroll_periods(worked_days),
		    "notes": "PRUEBA DE ENVIO DE NOMINA ELECTRONICA",
		    "worker": {
		        "type_worker_id": employee.type_worker_id._id,
		        "sub_type_worker_id": employee.sub_type_worker_id._id,
		        "payroll_type_document_identification_id": employee.payroll_type_document_identification_id._id,
		        "municipality_id": employee.municipality_id._id,
		        "type_contract_id": employee.type_contract_id._id,
		        "high_risk_pension": False,
		        "identification_number": employee.identification_number,
		        "surname": employee.surname,
		        "second_surname": employee.second_surname,
		        "first_name": employee.first_name,
		        "middle_name": employee.middle_name,
		        "address": employee.address,
		        "integral_salarary": employee.integral_salary,
		        "salary": employee.salary,
		        "email": employee.email
		    },
		    "payment": {
		        "payment_method_id": payment_form_employee.payment_method._id,
		        "bank_name": payment_form_employee.bank_name.name,
		        "account_type": payment_form_employee.account_type,
		        "account_number": str(payment_form_employee.account_number)
		    },
		    "accrued": {
		        "worked_days": worked_days,
		        "salary": f"{salary}",
		        "transportation_allowance": f"{transportation_allowance}",
		        "accrued_total": f"{accrued_total}"
		    },
		    "deductions": {
		        "eps_type_law_deductions_id": 1,
		        "eps_deduction": f"{eps_deduction}",
		        "pension_type_law_deductions_id": 5,
		        "pension_deduction": f"{pension_deduction}",
		        "deductions_total": f"{deductions_total}"
		    }
		}
		return cls.send_basic_payroll(payroll, employee, type_document, 
										data['accrued'] if 'accrued' in data and data['accrued'] else None, 
										data['deductions'] if 'deductions' in data and data['deductions'] else None, 
										data['total_accrued'] if 'total_accrued' in data and data['total_accrued'] else 0, 
										data['total_deductions'] if 'total_deductions' in data and data['total_deductions'] else 0
									)
	@staticmethod
	def send_basic_payroll(payroll, employee, type_document, accrued, deductions, total_accrued, total_deductions):
		result = False
		try:
			if accrued is not None:
				payroll['accrued'].update(accrued)
				payroll['accrued']['accrued_total'] = str(float(payroll['accrued']['accrued_total']) + float(total_accrued))
			if deductions is not None:
				payroll['deductions'].update(deductions)
				payroll['deductions']['deductions_total'] = str(float(payroll['deductions']['deductions_total']) + float(total_deductions))
			payroll_json = json.dumps(payroll, cls = NpEncoder)
			_data = {'type_document': type_document, 'pk_branch': employee.branch.pk}
			Resolution.add_number(_data)
			payroll = json.loads(payroll_json)
			payroll_instance = Payroll.objects.create(data_payroll = payroll, employee=employee, was_sent = True)
			message = "The payroll was sent to the DIAN successfully"
			payroll['cune'] = "afcab295862bf46813b009200d40d5e69f69ec589fab98578d6b2499b379f916fa97067dcd3eda45ee1eb8f044ba16fd"
			result = True
		except Exception as e:
		    print(e, 'Envio')
		    message = str(e)
		return {'result': result, 'message':message, 'data': payroll}

	@classmethod
	def delete_payroll(cls, data):
		result = False
		message = None
		payroll = None
		try:
			payroll_saved = cls.objects.get(employee = Employee.objects.get(pk = data['pk_employee']), cune = data['cune'])
			message = "This electronic payroll has already been eliminated"
			if not payroll_saved.annulled:
				value = payroll_saved.data_payroll
				type_document = 10
				payroll = {
					"type_document_id": type_document,
					"establishment_name": value['establishment_name'],
					"establishment_address": value['establishment_address'],
					"establishment_phone": value['establishment_phone'],
					"establishment_municipality": value['establishment_municipality'],
					"establishment_email": "alternate_email@alternate.com",
					"head_note": value['head_note'],
					"foot_note": value['foot_note'],
					"type_note": 2,
					"predecessor": {
					    "predecessor_number": value['consecutive'],
					    "predecessor_cune": data['cune'],
					    "predecessor_issue_date": value['period']['issue_date']
					},
					"period":{
					    "admision_date": value['period']['admision_date'],
					    "settlement_start_date": value['period']['settlement_start_date'],
					    "settlement_end_date": value['period']['settlement_end_date'],
					    "worked_time": value['period']['worked_time'],
					    "issue_date": value['period']['issue_date']
					},
					"prefix": "NA",
					"consecutive": Resolution.get_number(type_document),
					"payroll_period_id": value['payroll_period_id'],
					"notes": data['note']
				}
				payroll_saved.annulled = True
				payroll_saved.save()
				result = True
				message = "Electronic payroll successfully eliminated"
		except Exception as e:
			message = str(e)
		return {'result': result, 'message':message, 'data': payroll}