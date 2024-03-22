from django.db.models import Sum
from datetime import datetime, date
from django.db import IntegrityError
from django.db import models
import json, requests, env

class Operation(models.Model):
    url_api = models.CharField(max_length = 255)

class BANK_NAME(models.Model):
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name

class Transaction_Types(models.Model):
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name

class Book_Account(models.Model):
    name = models.CharField(max_length = 80)

    def __str__(self):
        return self.name

class Book_Account_Type(models.Model):
    name = models.CharField(max_length = 80)
    book_account = models.ForeignKey(Book_Account, on_delete= models.CASCADE)

    def __str__(self):
        return f'{self.name} - {self.book_account.name}'

class State(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 35)

    def __str__(self):
        return self.name

    @classmethod
    def get_state(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Municipalities(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 35)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_municipalities(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name,
                "pk_state": i.state.pk if i.state else "",
                "name_state": i.state.name if i.state else ""
            }
            for i in cls.objects.all()
        ]

class Type_Document_I(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 150)

    def __str__(self):
        return self.name

    @classmethod
    def get_type_document_i(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Type_Document(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name

    @classmethod
    def get_type_document(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Type_Organization(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name

    @classmethod
    def get_type_organization(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Type_Regimen(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name


    @classmethod
    def get_type_regimen(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Type_Contract(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name


    @classmethod
    def get_type_contract(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Payroll_Type_Document_Identification(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name


    @classmethod
    def get_payroll_type_document_identification(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Sub_Type_Worker(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name


    @classmethod
    def get_sub_type_worker(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Type_Worker(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name


    @classmethod
    def get_type_worker(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Payment_Form(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name

    @classmethod
    def get_list_payment_form(cls):
        return [
            {
                'pk' : i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Payment_Method(models.Model):
    _id = models.IntegerField()
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name
    
    @classmethod
    def get_list_payment_method(cls):
        return [
            {
                'pk' : i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]
        
class Permission(models.Model):
    _id = models.IntegerField(default = 1)
    name = models.CharField(max_length = 255)

    def __str__(self):
        return self.name

    @classmethod
    def get_list_permission(cls):
        return [
            {
                'pk_permission' : i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class CFDI(models.Model):
    name = models.CharField(max_length = 150, unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_cfdi(cls, data):
        message = "Success"
        result = True
        for i in data:
            try:
                cfdi = cls(name = data['name'])
                cfdi.save()
            except IntegrityError as e:
                message = str(e)
                result = False
        return {'message':message, 'result': result}

    @classmethod
    def get_list_cfdi(cls):
        return [
            {
                'pk' : i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class UnitMeasure(models.Model):
    name = models.CharField(max_length = 150, unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def create_um(cls, data):
        message = "Success"
        result = True
        for i in data:
            try:
                um = cls(name = data['name'])
                um.save()
            except IntegrityError as e:
                message = str(e)
                result = False
        return {'message':message, 'result': result}

    @classmethod
    def get_list_um(cls):
        return [
            {
                'pk' : i.pk,
                "name":i.name
            }
            for i in cls.objects.all().order_by("-id")
        ]

class Tax(models.Model):
    name = models.CharField(max_length = 150)
    tax_num = models.IntegerField(default=0)

    def __str__(self):
        return self.name+" "+str(self.tax_num)+"%"

    @classmethod
    def create_tax(cls, data):
        message = "Success"
        result = True
        for i in data:
            try:
                um = cls(name = data['name'], tax_num=data["tax"])
                um.save()
            except IntegrityError as e:
                message = str(e)
                result = False
        return {'message':message, 'result': result}

    @classmethod
    def get_list_tax(cls):
        return [
            {
                'pk' : i.pk,
                "name": i.name,
                "tax": i.tax_num
            }
            for i in cls.objects.all().order_by("-id")
        ]

class Send_Dian:
    def __init__(self, invoice):
        self.invoice = invoice

    def Error_Handling(self):
        message = None
        if self.days < 0:
            message = "La fecha de vencimiento o fecha de factura "


    def Data(self):
        tiempo_objeto = datetime.strptime(self.invoice['time'], "%H:%M:%S.%f")
        time = tiempo_objeto.strftime("%H:%M:%S")
        return {
            "number": self.invoice['number'],
            "type_document_id": self.type_document_id,
            "date": str(self.invoice['date']),
            "time": str(time),
            "resolution_number": self.invoice['resolution']['resolution'],
            "prefix": self.invoice['prefix'],
            "notes": self.invoice['note'],
            "disable_confirmation_text": True,
            "establishment_name": self.invoice['branch']['name'],
            "establishment_address": self.invoice['branch']['address'],
            "establishment_phone": self.invoice['branch']['phone'],
            "establishment_municipality": 1,
            "establishment_email": self.invoice['branch']['email'],
            "seze": "2021-2017",
            "foot_note": "Esta factura fue realizada por Evansoft",
        }

    def Billing_Reference(self):
        return {
            "number": self.invoice['number'],
            "uuid": self.invoice['number'],
            "issue_date": self.invoice['date']
        }

    def Customer(self):
        if str(self.invoice['customer']['identification_number'])[0:10] == "2222222222":
            return {
                "identification_number": 222222222222,
                "name": "CONSUMIDOR FINAL",
                "merchant_registration": "0000000-00"
            }
        else:
            return {
                "identification_number": self.invoice['customer']['identification_number'],
                "dv": self.invoice['customer']['dv'],
                "name": self.invoice['customer']['name'],
                "phone": self.invoice['customer']['phone'] if self.invoice['customer']['phone'] is not None else "12345678",
                "address": self.invoice['customer']['address'] if self.invoice['customer']['address'] is not None else "No tiene",
                "email": self.invoice['customer']['email'],
                "merchant_registration": "0000000-00",
                "type_document_identification_id": self.invoice['customer']['type_document_i'],
                "type_organization_id": self.invoice['customer']['type_organization'],
                "type_liability_id": 14,
                "municipality_id": self.invoice['customer']['municipality'],
                "type_regime_id": self.invoice['customer']['type_regime'],
                "postal_zone_code": 630001
            }

    def count_days(self, due_date):
        return (datetime.strptime(due_date, "%Y-%m-%d") - datetime.strptime(self.invoice['date'], "%Y-%m-%d")).days + 1

    def Payment_Form(self):
        self.days = self.count_days(self.invoice['payment_form']['payment_due_date'])
        return {
            "payment_form_id": self.invoice['payment_form']['payment_form'],
            "payment_method_id": self.invoice['payment_form']['payment_method'],
            "payment_due_date": self.invoice['payment_form']['payment_due_date'],
            "duration_measure": self.days
        }

    def sum_value(self, item):
        return sum(int(round(i[f'{item}'])) * round(int(i['quantity'])) for i in self.invoice['details'])

    def Legal_Monetary_Totals(self):
        subtotal = self.sum_value('price')
        ipo = self.sum_value('ipo')
        total_invoice = subtotal + self.sum_value('tax') + ipo        
        return {
            "line_extension_amount": subtotal,
            "tax_exclusive_amount": subtotal,
            "tax_inclusive_amount": total_invoice,
            "allowance_total_amount": '0',
            "charge_total_amount": '0',
            "payable_amount": total_invoice
        }

    def values_taxes(self,tax):
        total_base = 0
        total_tax = 0
        for item in self.invoice['details']:
            if int(tax) == int(item['tax_value']):
                total_tax += round((item['tax']  * item['quantity']))
                total_base += round((item['price'] * item['quantity']))
            if int(tax) == 15:
                total_tax += round((item['ipo']  * item['quantity']))
                total_base += round((item['price'] * item['quantity']))
        return {str(tax): total_tax, 'base': total_base}

    def Tax_Totals(self):
        taxes = []
        tax_19 = self.values_taxes(19)
        tax_5 = self.values_taxes(5)
        tax_0 = self.values_taxes(0)
        ipo_value = self.values_taxes(15)

        if tax_19['base'] != 0:
            taxes.append({
                "tax_id": 1,
                "tax_amount": str(tax_19['19']),
                "percent": "19",
                "taxable_amount": str(tax_19['base'])
            })
        if tax_5['base'] != 0:
            taxes.append({
                "tax_id": 1,
                "tax_amount": str(tax_5['5']),
                "percent": "5",
                "taxable_amount": str(tax_5['base'])
            })
        if tax_0['base'] != 0:
            taxes.append({
                "tax_id": 1,
                "tax_amount": str(tax_0['0']),
                "percent": "0",
                "taxable_amount": str(tax_0['base'])
            })
        if int(ipo_value['base']) != 0:
            taxes.append(
                {
                    "tax_id": 15,
                    "tax_amount": str(ipo_value['15']),
                    "taxable_amount": str(ipo_value['base']),
                    "percent": 0
                }
            )
        return taxes

    def Invoice_Lines(self):
        data = []
        for i in self.invoice['details']:
            quantity = float(i['quantity'])
            cost = round(float(i['price']) * quantity)
            tax = round(float(i['tax']) * quantity)
            ipo = round(float(i['ipo']) * quantity)

            total =  (cost + tax + ipo)
            
            data.append(
                {
                    "unit_measure_id": 70,
                    "invoiced_quantity": quantity,
                    "line_extension_amount": cost,
                    "free_of_charge_indicator": False,
                    "tax_totals": [
                        {
                            "tax_id": 1,
                            "tax_amount": tax,
                            "taxable_amount": cost,
                            "percent": i['tax_value']
                        },
                        {
                            "tax_id": 15,
                            "tax_amount": ipo,
                            "taxable_amount": cost,
                            "percent": 0
                        }
                    ],
                    "description": i['name'],
                    "notes": '',
                    "code": i['code'],
                    "type_item_identification_id": 4,
                    "price_amount": total,
                    "base_quantity": quantity,
                    "type_generation_transmition_id": 1,
                    "start_date": "2023-05-01"
                }
            )
        return data

    def Send(self, type_document):
        self.type_document_id = type_document
        document = "invoice"
        key_invoice = 'invoice_lines'
        key_customer = "customer"
        if type_document == 11:
            document = "support-document"
            key_customer = "seller"
        elif type_document == 4:
            document = "credit-note"
            key_invoice = "credit_note_lines"
        elif type_document == 5:
            document = "debit-note"
            key_invoice = "debit_note_lines"

        url = f"{env.URL_API}{document}"
        data = self.Data()
        data['payment_form'] = self.Payment_Form()
        data['legal_monetary_totals'] = self.Legal_Monetary_Totals()
        data['tax_totals'] = self.Tax_Totals()
        data[key_customer] = self.Customer()
        data[key_invoice] = self.Invoice_Lines()

        if type_document == 4 or type_document == 5:
            data['billing_reference'] = self.Billing_Reference()

        payload = json.dumps(data)
        headers = {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': f'Bearer {self.invoice["company"]["token"]}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = json.loads(response.text)
        result = False
        messages = []
        if 'errors' in response:
            for i,j in response['errors'].items():
                messages.append(response['errors'][i][0])
        else:
            print(response)
        return {'result':result, 'message':messages}



class Credi_Note_Product:
    def __init__(self, invoice, product, quantity, type_discrepancy, discrepancy_description, number_resolution):
        self.invoice = invoice
        self.product = product
        self.quantity = quantity
        self.type_discrepancy = type_discrepancy
        self.discrepancy_description = discrepancy_description
        self.number_resolution = number_resolution

    def header(self):
        return {
            "discrepancyresponsecode": self.type_discrepancy,
            "discrepancyresponsedescription": self.discrepancy_description,
            "notes": "PRUEBA DE NOTA CREDITO",
            "resolution_number": "0000000000",
            "prefix": "NCP",
            "number": self.number_resolution,
            "type_document_id": 4,
            "date": f"{date.today()}",
            "time": f"{datetime.now().strftime('%H:%M:%S')}",
            "establishment_name": self.invoice['branch']['name'],
            "establishment_address": self.invoice['branch']['address'],
            "establishment_phone": self.invoice['branch']['phone'],
            "establishment_municipality": 1,
            "establishment_email": self.invoice['branch']['email'],
            "seze": "2021-2017",
            "foot_note": "Esta factura fue realizada por Evansoft",
        }

    def sum_value(self, item):
        return sum(int(round(i[f'{item}'])) * round(int(i['quantity'])) for i in self.invoice['details'] if i['code'] == self.product)

    def Legal_Monetary_Totals(self):
        for i in self.invoice['details']:
            if i['code'] == self.product:
                subtotal = self.sum_value('price')
                ipo = self.sum_value('ipo')
                total_invoice = subtotal + self.sum_value('tax') + ipo        
                return {
                    "line_extension_amount": subtotal,
                    "tax_exclusive_amount": subtotal,
                    "tax_inclusive_amount": total_invoice,
                    "allowance_total_amount": '0',
                    "charge_total_amount": '0',
                    "payable_amount": total_invoice
                }

    def Customer(self):
        if str(self.invoice['customer']['identification_number'])[0:10] == "2222222222":
            return {
                "identification_number": 222222222222,
                "name": "CONSUMIDOR FINAL",
                "merchant_registration": "0000000-00"
            }
        else:
            return {
                "identification_number": self.invoice['customer']['identification_number'],
                "dv": self.invoice['customer']['dv'],
                "name": self.invoice['customer']['name'],
                "phone": self.invoice['customer']['phone'] if self.invoice['customer']['phone'] is not None else "12345678",
                "address": self.invoice['customer']['address'] if self.invoice['customer']['address'] is not None else "No tiene",
                "email": self.invoice['customer']['email'],
                "merchant_registration": "0000000-00",
                "type_document_identification_id": self.invoice['customer']['type_document_i'],
                "type_organization_id": self.invoice['customer']['type_organization'],
                "type_liability_id": 14,
                "municipality_id": self.invoice['customer']['municipality'],
                "type_regime_id": self.invoice['customer']['type_regime'],
                "postal_zone_code": 630001
            }

    def count_days(self, due_date):
        return (datetime.strptime(due_date, "%Y-%m-%d") - datetime.strptime(self.invoice['date'], "%Y-%m-%d")).days

    def Payment_Form(self):
        self.days = self.count_days(self.invoice['payment_form']['payment_due_date'])
        return {
            "payment_form_id": self.invoice['payment_form']['payment_form'],
            "payment_method_id": self.invoice['payment_form']['payment_method'],
            "payment_due_date": self.invoice['payment_form']['payment_due_date'],
            "duration_measure": self.days
        }

    def Billing_Reference(self):
        return {
            "number": self.invoice['number'],
            "uuid": self.invoice['cufe'],
            "issue_date": self.invoice['date']
        }

    def values_taxes(self,tax):
        total_base = 0
        total_tax = 0
        for item in self.invoice['details']:
            if item['code'] == self.product:
                if int(tax) == int(item['tax_value']):
                    total_tax += round((item['tax']  * item['quantity']))
                    total_base += round((item['price'] * item['quantity']))
                if int(tax) == 15:
                    total_tax += round((item['ipo']  * item['quantity']))
                    total_base += round((item['price'] * item['quantity']))
        return {str(tax): total_tax, 'base': total_base}

    def Tax_Totals(self):
        taxes = []
        for i in self.invoice['details']:
            if i['code'] == self.product:
                tax_19 = self.values_taxes(19)
                tax_5 = self.values_taxes(5)
                tax_0 = self.values_taxes(0)
                ipo_value = self.values_taxes(15)

                if tax_19['base'] != 0:
                    taxes.append({
                        "tax_id": 1,
                        "tax_amount": str(tax_19['19']),
                        "percent": "19",
                        "taxable_amount": str(tax_19['base'])
                    })
                if tax_5['base'] != 0:
                    taxes.append({
                        "tax_id": 1,
                        "tax_amount": str(tax_5['5']),
                        "percent": "5",
                        "taxable_amount": str(tax_5['base'])
                    })
                if tax_0['base'] != 0:
                    taxes.append({
                        "tax_id": 1,
                        "tax_amount": str(tax_0['0']),
                        "percent": "0",
                        "taxable_amount": str(tax_0['base'])
                    })
                if int(ipo_value['base']) != 0:
                    taxes.append(
                        {
                            "tax_id": 15,
                            "tax_amount": str(ipo_value['15']),
                            "taxable_amount": str(ipo_value['base']),
                            "percent": 0
                        }
                    )
        return taxes

    def Credit_Note_Lines(self):
        data = []
        for i in self.invoice['details']:
            if i['code'] == self.product:
                quantity = float(i['quantity'])
                cost = round(float(i['price']) * quantity)
                tax = round(float(i['tax']) * quantity)
                ipo = round(float(i['ipo']) * quantity)

                total =  (cost + tax + ipo)
                
                data.append(
                    {
                        "unit_measure_id": 70,
                        "invoiced_quantity": quantity,
                        "line_extension_amount": cost,
                        "free_of_charge_indicator": False,
                        "tax_totals": [
                            {
                                "tax_id": 1,
                                "tax_amount": tax,
                                "taxable_amount": cost,
                                "percent": i['tax_value']
                            },
                            {
                                "tax_id": 15,
                                "tax_amount": ipo,
                                "taxable_amount": cost,
                                "percent": 0
                            }
                        ],
                        "description": i['name'],
                        "notes": '',
                        "code": i['code'],
                        "type_item_identification_id": 4,
                        "price_amount": total,
                        "base_quantity": quantity,
                        "type_generation_transmition_id": 1,
                        "start_date": "2023-05-01"
                    }
                )
        return data

    def Send(self):
        url = f"{env.URL_API}credit-note"
        data = self.header()
        data['billing_reference'] = self.Billing_Reference()
        data['payment_form'] = self.Payment_Form()
        data['legal_monetary_totals'] = self.Legal_Monetary_Totals()
        data['tax_totals'] = self.Tax_Totals()
        data["customer"] = self.Customer()
        data["credit-note"] = self.Credit_Note_Lines()
        payload = json.dumps(data)
        return True
        headers = {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': f'Bearer {self.invoice["company"]["token"]}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = json.loads(response.text)
        result = False
        messages = []
        if 'errors' in response:
            for i,j in response['errors'].items():
                messages.append(response['errors'][i][0])
        else:
            print(response)
        return {'result':result, 'message':messages}

