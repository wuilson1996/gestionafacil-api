from django.db.models import Sum
from datetime import datetime, date
from django.db import IntegrityError
from django.db import models
import json, requests, env
from django.core import serializers

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
    _id = models.IntegerField(null = True, blank = True)
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
    _id = models.IntegerField(null = True, blank = True)
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
    code = models.CharField(max_length = 100, blank=True, null=True)
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name+" | "+str(self.code)


    @classmethod
    def get_type_regimen(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name,
                "code":i.code
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

class EmailSMTP(models.Model):
    email = models.CharField(max_length = 100)
    password = models.CharField(max_length = 100)
    host = models.CharField(max_length = 100)
    port = models.CharField(max_length = 100)

    def __str__(self):
        return self.email


    @classmethod
    def get_email(cls):
        return [
            {
                'pk':i.pk,
                "email":i.email,
                "host":i.host,
                "port":i.port
            }
            for i in cls.objects.all()
        ]

class MessageEmail(models.Model):
    asunto = models.CharField(max_length = 256)
    message = models.TextField()
    CHECK_EMAIL = "CheckEmail"
    SEND_FILE = "SendFile"
    TYPE = (
        (CHECK_EMAIL, "CheckEmail"),
        (SEND_FILE, "SendFile"),
    )
    type_message = models.TextField(choices=TYPE, default=CHECK_EMAIL)

    def __str__(self):
        return self.asunto


    @classmethod
    def get_email(cls):
        return [
            {
                'pk':i.pk,
                "asunto":i.asunto,
                "message":i.message,
                "type_message":i.type_message,
            }
            for i in cls.objects.all()
        ]

class PostalCode(models.Model):
    code = models.CharField(max_length = 100)
    municipality = models.ForeignKey(Municipalities, on_delete=models.CASCADE)

    def __str__(self):
        return self.code

    @classmethod
    def get_postal_code(cls, code):
        result = {
            "data": [],
			"code": 200,
			"status": "OK",
		}
        for i in cls.objects.filter(code=code):
            c = []
            for cl in Colonia.objects.filter(postal_code = i):
                c.append({
                    "pk": cl.pk,
                    "name": cl.name
                })
            result["data"].append({
                'pk':i.pk,
                "code":i.code,
                "municipality":i.municipality.name,
                "municipality_id":i.municipality.pk,
                "state":i.municipality.state.name,
                "state_id":i.municipality.state.pk,
                "colonia":c
            })
        return result

class Colonia(models.Model):
    name = models.CharField(max_length = 100)
    postal_code = models.ForeignKey(PostalCode, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

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

class Sector(models.Model):
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name

    @classmethod
    def get_sector(cls):
        return [
            {
                'pk':i.pk,
                "name":i.name
            }
            for i in cls.objects.all()
        ]

class Payment_Form(models.Model):
    _id = models.CharField(max_length= 20, blank=True, null=True)
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
    code = models.CharField(max_length= 20, blank=True, null=True)
    name = models.CharField(max_length = 50)

    def __str__(self):
        return self.name+" | "+self.code
    
    @classmethod
    def get_list_payment_method(cls):
        return [
            {
                'pk' : i.pk,
                "name":i.name,
                "code":i.code
            }
            for i in cls.objects.all().order_by("-id")
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

class ClaveProdServ(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length = 150)
    palabrasSimilares = models.CharField(max_length = 150)
    estimuloFranjaFronteriza = models.CharField(max_length = 150)
    fechaFinVigencia = models.CharField(max_length = 150)
    fechaInicioVigencia = models.CharField(max_length = 150)
    complementoQueDebeIncluir = models.CharField(max_length = 150)
    incluirIEPSTrasladado = models.CharField(max_length = 150)
    incluirIVATrasladado = models.CharField(max_length = 150)

    def __str__(self):
        return self.code+" | "+self.name

    @classmethod
    def create_clave_prod_serv(cls, data):
        message = "Success"
        result = True
        for i in data:
            try:
                cfdi = cls(name = data['name'], code = data["code"])
                cfdi.save()
            except IntegrityError as e:
                message = str(e)
                result = False
        return {'message':message, 'result': result}

    @classmethod
    def get_list_clave_prod_serv(cls):
        return [
            {
                'pk' : i.pk,
                "name":str(i.name).replace('"', "'"),
                "code":i.code
            }
            for i in cls.objects.all()
        ]

class MotivoCancel(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length = 150)

    def __str__(self):
        return self.code+" | "+self.name

    @classmethod
    def create_motivo_cancel(cls, data):
        message = "Success"
        result = True
        for i in data:
            try:
                cfdi = cls(name = data['name'], code = data["code"])
                cfdi.save()
            except IntegrityError as e:
                message = str(e)
                result = False
        return {'message':message, 'result': result}

    @classmethod
    def get_list_motivo_cancel(cls):
        return [
            {
                'pk' : i.pk,
                "name":i.name,
                "code":i.code
            }
            for i in cls.objects.all()
        ]

class CFDI(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length = 150)

    def __str__(self):
        return self.code+" | "+self.name

    @classmethod
    def create_cfdi(cls, data):
        message = "Success"
        result = True
        for i in data:
            try:
                cfdi = cls(name = data['name'], code = data["code"])
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
                "name":i.name,
                "code":i.code
            }
            for i in cls.objects.all()
        ]

class UnitMeasure(models.Model):
    name = models.CharField(max_length = 150, unique=True)
    clave = models.CharField(max_length = 150)
    tipo = models.CharField(max_length = 150)

    def __str__(self):
        return str(self.name)+" | Clave: "+str(self.clave)+" | Tipo: "+str(self.tipo)

    @classmethod
    def create_um(cls, data):
        message = "Success"
        result = True
        for i in data:
            try:
                um = cls(name = data['name'], clave = data["clave"], tipo = data["tipo"])
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
                "name":i.name,
                "clave":i.clave,
                "tipo":i.tipo
            }
            for i in cls.objects.all().order_by("-id")
        ]

class List_Price(models.Model):
    name = models.CharField(max_length = 50)
    percent = models.IntegerField()
    principal = models.BooleanField(default=False)
    VALOR = "valor"
    PORCENTAJE = "porcentaje"
    TYPE = (
        (VALOR, "valor"),
        (PORCENTAJE, "porcentaje")
    )
    type_price = models.TextField(choices=TYPE, default="valor")
    description = models.TextField()
    branch = models.IntegerField()
    
    def __str__(self):
        return f'{self.name} - {self.percent} by Branch: {self.branch}'
    
    @classmethod
    def create_price(cls, data):
        from user.models import Employee
        result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
        if Employee.check_by_token(token=data["token"]):
            employee = Employee.search_by_token(token=data["token"])
            try:
                price = cls.objects.filter(pk = data["pk_price"]).first()
                if not price:
                    price = cls.objects.create(
                        name = data["name"],
                        percent = data["percent"],
                        principal = data["principal"],
                        type_price = data["type"],
                        branch = employee.branch.pk,
                        description = data["description"]
                    )
                    HistoryGeneral.create_history(
                        action=HistoryGeneral.CREATED,
                        class_models=HistoryGeneral.LIST_PRICE,
                        class_models_json=json.loads(serializers.serialize('json', [price]))[0],
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
                else:
                    price.name = data["name"]
                    price.percent = data["percent"]
                    price.type_price = data["type"]
                    price.description = data["description"]
                    price.save()
                    HistoryGeneral.create_history(
                        action=HistoryGeneral.UPDATE,
                        class_models=HistoryGeneral.LIST_PRICE,
                        class_models_json=json.loads(serializers.serialize('json', [price]))[0],
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
                result["code"] = 200
                result["status"] = "OK"
                result["message"] = "Success"
            except Exception as e:
                result["message"] = str(e)
        return result

    @classmethod
    def get_list_price(cls, data):
        from user.models import Employee
        result = {
            "data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
        if Employee.check_by_token(token=data["token"]):
            employee = Employee.search_by_token(token=data["token"])
            for p in cls.objects.filter(branch = employee.branch.pk):
                result["data"].append({
                    "pk": p.pk,
                    "name": p.name,
                    "percent": p.percent,
                    "principal": p.principal,
                    "type_price": p.type_price,
                    "description": p.description
                })
            result["code"] = 200
            result["message"] = "Success"
            result["status"] = "OK"
        return result
    
    @classmethod
    def delete_list_price(cls, data):
        from user.models import Employee
        result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
        if Employee.check_by_token(token=data["token"]):
            employee = Employee.search_by_token(token=data["token"])
            list_price = List_Price.objects.filter(pk = data["pk_price"]).first()
            HistoryGeneral.create_history(
                action=HistoryGeneral.DELETE,
                class_models=HistoryGeneral.LIST_PRICE,
                class_models_json=json.loads(serializers.serialize('json', [list_price]))[0],
                employee=employee.pk,
                username=employee.user_django.username,
                branch=employee.branch.pk
            )
            list_price.delete()
            result["code"] = 200
            result["message"] = "Success"
            result["status"] = "OK"
        return result

class Tax(models.Model):
    name = models.CharField(max_length = 150)
    tax_num = models.FloatField(default=0)
    description = models.TextField()
    TYPE = (
        ("IVA", "IVA"),
        ("Otro", "Otro"),
        ("Local", "Local"),
        ("IEPS", "IEPS"),
        ("IVA Exento", "IVA Exento"),
        ("IEPS Exento", "IEPS Exento"),
        ("Retencion de ISR", "Retencion de ISR"),
        ("Retencion de IVA", "Retencion de IVA"),
        ("Retencion de IVA por fletes", "Retencion de IVA por fletes"),
        ("Otro tipo de retencion", "Otro tipo de retencion"),
        ("Retencion local", "Retencion local"),
    )
    acreditable = models.BooleanField(default=True)
    type_tax = models.TextField(choices=TYPE, default="IVA")
    PATH = (
        ("tax", "tax"),
        ("retention", "retention"),
    )
    path = models.TextField(max_length=30, choices=PATH, default="tax")
    branch = models.IntegerField()

    def __str__(self):
        return self.name+" "+str(self.tax_num)+"%"

    @classmethod
    def create_tax(cls, data):
        from user.models import Employee
        result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
        if Employee.check_by_token(token=data["token"]):
            employee = Employee.search_by_token(token=data["token"])
            try:
                _tax = cls.objects.filter(pk = data["pk"]).first()
                if not _tax:
                    _tax = cls(
                        name = data['name'],
                        tax_num=data["tax"],
                        description=data["description"],
                        acreditable=data["acreditable"],
                        type_tax=data["type"],
                        branch=employee.branch.pk,
                        path=data["path"]
                    )
                    option = HistoryGeneral.TAX
                    if data["path"] != "tax":
                        option = HistoryGeneral.RETENTION
                    HistoryGeneral.create_history(
                        action=HistoryGeneral.CREATED,
                        class_models=option,
                        class_models_json=json.loads(serializers.serialize('json', [_tax]))[0],
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
                else:
                    _tax.name = data["name"]
                    _tax.tax_num = data["tax"]
                    _tax.description = data["description"]
                    _tax.acreditable = data["acreditable"]
                    _tax.type_tax = data["type"]
                    option = HistoryGeneral.TAX
                    if data["path"] != "tax":
                        option = HistoryGeneral.RETENTION
                    HistoryGeneral.create_history(
                        action=HistoryGeneral.UPDATE,
                        class_models=option,
                        class_models_json=json.loads(serializers.serialize('json', [_tax]))[0],
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
                _tax.save()
                result["code"] = 200
                result["status"] = "OK"
                result["message"] = "Success"
            except IntegrityError as e:
                result["message"] = str(e)
        return result

    @classmethod
    def get_list_tax(cls, data):
        from user.models import Employee
        result = {
            "data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
        if Employee.check_by_token(token=data["token"]):
            employee = Employee.search_by_token(token=data["token"])
            result["data"] = [
                {
                    'pk' : i.pk,
                    "name": i.name,
                    "tax": i.tax_num,
                    "description": i.description,
                    "acreditable": i.acreditable,
                    "type": i.type_tax,
                    "path": i.path
                }
                for i in cls.objects.filter(branch=employee.branch.pk, path=data["path"]).order_by("-id")
            ]
            result["code"] = 200
            result["status"] = "OK"
            result["message"] = "Success"
        #print(result)
        return result

    @classmethod
    def delete_tax(cls, data):
        from user.models import Employee
        result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
        try:
            if Employee.check_by_token(token=data["token"]):
                employee = Employee.search_by_token(token=data["token"])
                _tax = cls.objects.filter(pk = data["pk"])
                HistoryGeneral.create_history(
                    action=HistoryGeneral.DELETE,
                    class_models=HistoryGeneral.TAX,
                    class_models_json=json.loads(serializers.serialize('json', [_tax.first()]))[0],
                    employee=employee.pk,
                    username=employee.user_django.username,
                    branch=employee.branch.pk
                )
                _tax.delete()
                result["code"] = 200
                result["message"] = "Success"
                result["status"] = "OK"
        except IntegrityError as e:
            result["message"] = str(e)
        return result

class TermPayment(models.Model):
    name = models.CharField(max_length = 150)
    days = models.IntegerField(default=0)
    branch = models.IntegerField()

    def __str__(self):
        return self.name+" "+str(self.days)

    @classmethod
    def create_term(cls, data):
        from user.models import Employee
        result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
        if Employee.check_by_token(token=data["token"]):
            employee = Employee.search_by_token(token=data["token"])
            try:
                term = cls.objects.filter(pk = data["pk"]).first()
                if not term:
                    term = cls(name = data['name'], days=data["days"], branch=employee.branch.pk)
                    HistoryGeneral.create_history(
                        action=HistoryGeneral.CREATED,
                        class_models=HistoryGeneral.TERMPAYMENT,
                        class_models_json=json.loads(serializers.serialize('json', [term]))[0],
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
                else:
                    term.name = data["name"]
                    term.days = data["days"]
                    HistoryGeneral.create_history(
                        action=HistoryGeneral.UPDATE,
                        class_models=HistoryGeneral.TERMPAYMENT,
                        class_models_json=json.loads(serializers.serialize('json', [term]))[0],
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
                term.save()
                result["code"] = 200
                result["status"] = "OK"
                result["message"] = "Success"
            except IntegrityError as e:
                result["message"] = str(e)
        return result

    @classmethod
    def get_list_term(cls, data):
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
                    'pk' : i.pk,
                    "name": i.name,
                    "days": i.days
                }
                for i in cls.objects.filter(branch=employee.branch.pk).order_by("-id")
            ]
            result["code"] = 200
            result["status"] = "OK"
            result["message"] = "Success"
        return result

    @classmethod
    def delete_term(cls, data):
        from user.models import Employee
        result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
        try:
            if Employee.check_by_token(token=data["token"]):
                employee = Employee.search_by_token(token=data["token"])
                term = cls.objects.filter(pk = data["pk"])
                HistoryGeneral.create_history(
                    action=HistoryGeneral.DELETE,
                    class_models=HistoryGeneral.TERMPAYMENT,
                    class_models_json=json.loads(serializers.serialize('json', [term.first()]))[0],
                    employee=employee.pk,
                    username=employee.user_django.username,
                    branch=employee.branch.pk
                )
                term.delete()
                result["code"] = 200
                result["message"] = "Success"
                result["status"] = "OK"
        except IntegrityError as e:
            result["message"] = str(e)
        return result

class TermAndCond(models.Model):
    description = models.TextField()
    notas = models.TextField()
    pie_invoice = models.TextField(default="")
    state_account = models.BooleanField(default=False)
    branch = models.IntegerField()

    def __str__(self):
        return self.description+" "+str(self.notas)

    @classmethod
    def create_term(cls, data):
        from user.models import Employee
        result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
        if Employee.check_by_token(token=data["token"]):
            employee = Employee.search_by_token(token=data["token"])
            try:
                term = cls.objects.filter(pk = data["pk"]).first()
                if not term:
                    term = cls.objects.create(
                        description = data['description'], 
                        notas=data["notas"], 
                        pie_invoice=data["pie_invoice"], 
                        state_account=data["state_account"], 
                        branch=employee.branch.pk
                    )
                    HistoryGeneral.create_history(
                        action=HistoryGeneral.CREATED,
                        class_models=HistoryGeneral.TERMANDCOND,
                        class_models_json=json.loads(serializers.serialize('json', [term]))[0],
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
                else:
                    term.description = data["description"]
                    term.notas = data["notas"]
                    term.pie_invoice = data["pie_invoice"]
                    term.state_account = data["state_account"]
                    HistoryGeneral.create_history(
                        action=HistoryGeneral.UPDATE,
                        class_models=HistoryGeneral.TERMANDCOND,
                        class_models_json=json.loads(serializers.serialize('json', [term]))[0],
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
                term.save()
                result["code"] = 200
                result["status"] = "OK"
                result["message"] = "Success"
            except IntegrityError as e:
                result["message"] = str(e)
        return result

    @classmethod
    def get_term(cls, data):
        from user.models import Employee
        result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
            "data": {"pk": 0}
		}
        if Employee.check_by_token(token=data["token"]):
            employee = Employee.search_by_token(token=data["token"])
            term = cls.objects.filter(branch=employee.branch.pk).first()
            if term:
                result["data"] = {
                    'pk' : term.pk,
                    "description": term.description,
                    "notas":term.notas,
                    "pie_invoice": term.pie_invoice,
                    "state_account": term.state_account
                }
            result["code"] = 200
            result["status"] = "OK"
            result["message"] = "Success"
        return result

class SellerInfo(models.Model):
    name = models.CharField(max_length = 150)
    rfc = models.TextField(max_length=200)
    observation = models.TextField()
    branch = models.IntegerField()

    def __str__(self):
        return self.name+" "+str(self.rfc)

    @classmethod
    def create_seller(cls, data):
        from user.models import Employee
        result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
        if Employee.check_by_token(token=data["token"]):
            employee = Employee.search_by_token(token=data["token"])
            try:
                seller = cls.objects.filter(pk = data["pk"]).first()
                if not seller:
                    seller = cls(name = data['name'], rfc=data["rfc"], observation=data["observation"], branch=employee.branch.pk)
                    HistoryGeneral.create_history(
                        action=HistoryGeneral.CREATED,
                        class_models=HistoryGeneral.SELLER,
                        class_models_json=json.loads(serializers.serialize('json', [seller]))[0],
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
                else:
                    seller.name = data["name"]
                    seller.rfc = data["rfc"]
                    seller.observation = data["observation"]
                    HistoryGeneral.create_history(
                        action=HistoryGeneral.UPDATE,
                        class_models=HistoryGeneral.SELLER,
                        class_models_json=json.loads(serializers.serialize('json', [seller]))[0],
                        employee=employee.pk,
                        username=employee.user_django.username,
                        branch=employee.branch.pk
                    )
                seller.save()
                result["code"] = 200
                result["status"] = "OK"
                result["message"] = "Success"
            except IntegrityError as e:
                result["message"] = str(e)
        return result

    @classmethod
    def get_list_seller(cls, data):
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
                    'pk' : i.pk,
                    "name": i.name,
                    "rfc": i.rfc,
                    "observation": i.observation,
                    "branch": i.branch
                }
                for i in cls.objects.filter(branch=employee.branch.pk).order_by("-id")
            ]
            result["code"] = 200
            result["status"] = "OK"
            result["message"] = "Success"
        return result

    @classmethod
    def delete_seller(cls, data):
        from user.models import Employee
        result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
        try:
            if Employee.check_by_token(token=data["token"]):
                employee = Employee.search_by_token(token=data["token"])
                _seller = cls.objects.filter(pk = data["pk"])
                HistoryGeneral.create_history(
					action=HistoryGeneral.DELETE,
					class_models=HistoryGeneral.SELLER,
					class_models_json=json.loads(serializers.serialize('json', [_seller.first()]))[0],
					employee=employee.pk,
					username=employee.user_django.username,
					branch=employee.branch.pk
				)
                _seller.delete()
                result["code"] = 200
                result["message"] = "Success"
                result["status"] = "OK"
        except IntegrityError as e:
            result["message"] = str(e)
        return result

class Notification(models.Model):
    asunto = models.CharField(max_length = 150)
    description = models.TextField()
    branch = models.IntegerField()
    name = models.CharField(max_length=256)
    check = models.CharField(max_length=256)
    days = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    OPTION = (
        ("template", "template"),
        ("notify", "notify"),
    )
    option = models.TextField(max_length=30, choices=OPTION, default="notify")

    def __str__(self):
        return self.asunto

    @classmethod
    def create_notification(cls, data):
        from user.models import Employee
        result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
		}
        if Employee.check_by_token(token=data["token"]):
            employee = Employee.search_by_token(token=data["token"])
            try:
                notify = cls.objects.filter(pk = data["pk"]).first()
                if notify:
                    notify.asunto = data["asunto"]
                    notify.description = data["description"]
                    notify.save()
                else:
                    notify = cls.objects.create(
                        asunto = data["asunto"],
                        description = data["description"],
                        branch = employee.branch.pk,
                        name = data["name"],
                        check = data["check"],
                        days = data["days"],
                        option = data["option"]
                    )

                HistoryGeneral.create_history(
					action=HistoryGeneral.CREATED,
					class_models=HistoryGeneral.NOTIFICATION,
					class_models_json=json.loads(serializers.serialize('json', [notify]))[0],
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
    def change_notification(cls, data):
        from user.models import Employee
        result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
		}
        if Employee.check_by_token(token=data["token"]):
            employee = Employee.search_by_token(token=data["token"])
            try:
                notify = cls.objects.filter(pk = data["pk"]).first()
                if notify:
                    notify.active = not notify.active
                    notify.days = data["days"]
                    notify.save()

                HistoryGeneral.create_history(
					action=HistoryGeneral.UPDATE,
					class_models=HistoryGeneral.NOTIFICATION,
					class_models_json=json.loads(serializers.serialize('json', [notify]))[0],
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
    def get_list_notification(cls, data):
        from user.models import Employee
        result = {
			"code": 400,
			"status": "Fail",
			"message": "Token no valido",
            "data": []
		}
        if Employee.check_by_token(token=data["token"]):
            employee = Employee.search_by_token(token=data["token"])
            result["data"] = [
                {
                    'pk' : i.pk,
                    "asunto":i.asunto,
                    "description":i.description,
                    "branch": i.branch,
                    "name": i.name,
                    "check": i.check,
                    "days": i.days,
                    "active": i.active,
                    "option": i.option
                }
                for i in cls.objects.filter(branch=employee.branch.pk, option=data["option"])
            ]
            result["code"] = 200
            result["message"] = "Success"
            result["status"] = "OK"
        return result

class HistoryGeneral(models.Model):
    CREATED = 'Created'
    UPDATE = 'Update'
    DELETE = 'Delete'
    ANNULLED = 'Annulled'
    ACTION_CHOICES = (
	    (CREATED, 'Created'),
	    (UPDATE, 'Update'),
	    (DELETE, 'Delete'),
	    (ANNULLED, 'Annulled'),
	)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, null = True, blank = True)
    CUSTOMER = 'Customer'
    INVENTORY = 'Inventory'
    INVOICE = 'Invoice'
    INVOICE_PROVIDER = 'Invoice_provider'
    REMISSION = 'Remission'
    COTIZATION = 'Cotization'
    SERVICE = 'Service'
    PROVIDER = 'Provider'
    SPENT = 'Spent'
    EMPLOYEE = 'Employee'
    STORE = 'Store'
    EMPRESA = 'Empresa'
    TERMPAYMENT = 'TermPayment'
    TERMANDCOND = 'TermAndCond'
    RESOLUTION = 'Resolution'
    SELLER = 'Seller'
    TAX = 'Tax'
    RETENTION = 'Retention'
    TEMPLATE = 'Template'
    NOTIFICATION = 'Notification'
    ACCOUNTING = 'Accounting'
    SUSCRIPTION = 'Suscription'
    BRANCH = 'Branch'
    LIST_PRICE = 'List_price'
    CATEGORY = "Category"
    ORDER_BUY = "Order_buy"
    Bill_TO_PAY = "Bil_to_pay"
    PAYMENT_INVOICE = "Payment_invoice"
    PAYMENT_TO_PAY = "Payment_to_pay"
    BANK = "Bank"
    CLASS_MODELS_CHOICES = (
	    (CUSTOMER, 'Customer'),
	    (INVENTORY, 'Inventory'),
	    (INVOICE, 'Invoice'),
	    (REMISSION, 'Remission'),
        (COTIZATION, 'Cotization'),
        (SERVICE, 'Service'),
        (PROVIDER, 'Provider'),
        (SPENT, 'Spent'), #Gasto
        (EMPLOYEE, 'Employee'),
        (STORE, 'Store'),
        (EMPRESA, 'Empresa'),
        (TERMPAYMENT, 'TermPayment'),
        (TERMANDCOND, 'TermAndCond'),
        (RESOLUTION, 'Resolution'),
        (SELLER, 'Seller'),
        (TAX, 'Tax'),
        (RETENTION, 'Retention'),
        (TEMPLATE, 'Template'),
        (NOTIFICATION, 'Notification'),
        (ACCOUNTING, 'Accounting'),
        (SUSCRIPTION, 'Suscription'),
        (BRANCH, 'Branch'),
        (LIST_PRICE, 'List_price'),
        (CATEGORY, "Category"),
        (ORDER_BUY, "Order_buy"),
        (INVOICE_PROVIDER, "Invoice_provider"),
        (Bill_TO_PAY, "Bil_to_pay"),
        (PAYMENT_INVOICE, "Payment_invoice"),
        (PAYMENT_TO_PAY, "Payment_to_pay"),
        (BANK, BANK),
	)
    class_models = models.CharField(max_length=50, choices=CLASS_MODELS_CHOICES, null = True, blank = True) # customer, inventory, invoice, etc.
    class_models_json = models.JSONField()
    employee = models.IntegerField()
    username = models.CharField(max_length=100)
    created = models.DateTimeField()
    branch = models.IntegerField() # id branch.

    @classmethod
    def create_history(cls, action, class_models, class_models_json, employee, username, branch):
        cls.objects.create(
            action = action,
            class_models = class_models,
            class_models_json = class_models_json,
            employee = employee,
            username = username,
            created = datetime.now(),
            branch = branch
        )

    @classmethod
    def get_history(cls, data):
        from user.models import Employee
        result = {
			"data": [],
			"code": 400,
			"status": "Fail",
			"message": "Token no valido"
		}
        if Employee.check_by_token(token=data["token"]):
            employee = Employee.search_by_token(token=data["token"])
            for h in cls.objects.filter(branch = employee.branch.pk).order_by("-id"):
                result['data'].append({
					"pk": h.pk,
					"action": h.action,
					"class_models": h.class_models,
					"class_models_json": h.class_models_json,
					"employee": h.employee,
                    "username": h.username,
                    "created": h.created,
                    "branch": h.branch
				})
            result['code'] = 200
            result['message'] = ""
            result["status"] = "OK"
        
        return result
    

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

