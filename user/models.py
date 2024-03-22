from django.utils.crypto import get_random_string
from django.db import models
from company.models import Branch, License
from setting.models import *
from django.core import serializers
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
import json, env


class Employee(models.Model):
    type_worker_id = models.ForeignKey(Type_Worker, on_delete = models.CASCADE, null = True, blank = True)
    sub_type_worker_id = models.ForeignKey(Sub_Type_Worker, on_delete = models.CASCADE, null = True, blank = True)
    payroll_type_document_identification_id = models.ForeignKey(Payroll_Type_Document_Identification, on_delete = models.CASCADE, null = True, blank = True)
    municipality_id = models.ForeignKey(Municipalities, on_delete = models.CASCADE, null = True, blank = True)
    type_contract_id = models.ForeignKey(Type_Contract, on_delete = models.CASCADE, null = True, blank = True)
    high_risk_pension = models.BooleanField(default = False)
    identification_number = models.IntegerField()
    surname = models.CharField(max_length=255)
    second_surname = models.CharField(max_length=255, null = True, blank = True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255)
    integral_salary = models.BooleanField(default = True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField(null = True, blank = True)
    branch = models.ForeignKey(Branch, on_delete = models.CASCADE, null = True, blank = True)
    user_name = models.CharField(max_length = 20, null = True, blank = True)
    psswd = models.CharField(max_length = 20, default = get_random_string(length=20))
    block = models.BooleanField(default = False)
    login_attempts = models.PositiveIntegerField(default=0)
    permission = models.ManyToManyField(Permission, blank = True, null = True)
    active = models.BooleanField(default = False)
    internal_email = models.EmailField(null=True, blank=True, unique= True)
    user_django = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True)


    @classmethod
    def create_user_django(cls, data):
        result = {
            "code": 400,
            "status": "Fail",
            "message": "Token no valido"
        }
        try:
            user = User.objects.create_user(username=data['username'], email=data['email'])
            user.set_password(data['psswd'])
            user.save()
            result["code"] = 200
            result["status"] = "OK"
            result["message"] = "Success"
        except Exception as e:
            result['message'] = str(e)
        return result


    @staticmethod
    def search_by_token(token):
        return Employee.objects.get(user_django = Token.objects.get(key = token).user)
    
    @staticmethod
    def check_by_token(token):
        return True if Token.objects.filter(key = token).first() else False
    
    @staticmethod
    def delete_token(token):
        Token.objects.filter(key = token).delete()

    @classmethod
    def get_list_email(cls, data):
        _data = []
        branch = Branch.objects.get(pk = data['pk_branch'])
        for i in Branch.objects.filter(company = branch.company):
            e = cls.objects.filter(branch = i)
            for j in e:
                if j.internal_email is not None:
                    _data.append({
                        "pk_employee": j.pk,
                        "internal_email": j.internal_email,
                        })
        return _data

    def __str__(self):
        return f"{self.first_name} {self.surname}"

    @classmethod
    def query_permissions(cls, data):
        return [i.name for i in cls.search_by_token(data['token']).permission.all()]


    @classmethod
    def Update_User(cls, data):
        result = {
            "data": {},
            "code": 400,
            "status": "Fail",
            "message": "Token no valido"
        }
        try:
            
            e = cls.search_by_token(data['token'])
            validate = License.validate_date(e.branch)
            if validate['result']:
                e.type_worker_id = Type_Worker.objects.get(id = data['type_worker_id'])
                e.payroll_type_document_identification_id = Payroll_Type_Document_Identification.objects.get(id = data['payroll_type_document_identification_id'])
                e.municipality_id = Municipalities.objects.get(id = data['municipality_id'])
                e.type_contract_id = Type_Contract.objects.get(id = data['type_contract_id'])
                e.identification_number = data['identification_number']
                e.surname = data['surname']
                e.second_surname = data['second_surname']
                e.first_name = data['names'] 
                e.address = data['address']
                # e.integral_salary = data['integral_salary']
                e.salary = data['salary']
                e.email = data['email']
                e.branch = e.branch
                e.user_name = data['user_name'].lower()
                e.psswd = get_random_string(length=20) if data['psswd'] is None else data['psswd']
                e.save()
                e.permission.clear()
                for i in data['permissions']:
                    e.permission.add(Permission.objects.get(pk=i)) 
                result['code'] = 200
                result['status'] = 'OK'
                result['message'] = "Success"
            else:
                result['message'] = validate['message']
        except cls.DoesNotExist as e:
            result['message'] = str(e)
            e = None
        return result


    @classmethod
    def login(cls, data):
        result = {
            "code": 400,
            "status": "Fail",
            "message": "Token no valido"
        }
        employee = None
        user = authenticate(username=data['user'], password=data['psswd'])
        if user:
            token, created = Token.objects.get_or_create(user=user)
            employee = cls.objects.filter(user_django = user).first()
            if employee is not None:
                if not employee.active:
                    validate = License.validate_date(employee.branch)
                    if validate['result']:
                        result['code'] = 200
                        result['message'] = "Success"
                        result['status'] = 'OK'
                        #employee.active = True
                        #employee.save()
                        result["data"] = {
                            'pk_employee': employee.pk,'token': str(token.key), 'name': f"{employee.first_name} {employee.surname}",
                            "pk_branch":employee.branch.pk, "name_branch": employee.branch.name, 'logo': env.URL_LOCAL + employee.branch.company.logo.url, "check": True
                        }
                        result["data"]['permission'] = [ i.name for i in employee.permission.all()]
                    else:
                        result['message'] = validate['message']
                else:
                    result['message'] = "Ya tiene la cuenta abierta en otro dispositivo"
            else:
                result["data"] = {'token': str(token.key), "check": False}
                result['code'] = 200
                result['message'] = "Employee no ha sido configurado"
                result['status'] = 'Employee'
        else:
            result['message'] = "Usuario o clave incorrecto"
        return result

    @classmethod
    def logout(cls, data):
        result = {
            "code": 400,
            "status": "Fail",
            "message": "Token no valido"
        }
        try:
            if cls.check_by_token(data['token']):
                try:
                    employee = cls.search_by_token(data['token'])
                    employee.active = False
                    employee.save()
                except Exception as e2:
                    pass
                cls.delete_token(data['token'])
                result['code'] = 200
                result['status'] = 'OK'
                result['message'] = "Success"
            else:
                result["message"] = "Token not valid"
        except Exception as e:
            result['message'] = str(e)
        return result

    @classmethod
    def create_employee(cls, data):
        result = {
            "data": {},
            "code": 400,
            "status": "Fail",
            "message": "Token no valido"
        }
        try:
            employee = cls.objects.get(identification_number=data['identification_number'])
            result['message'] = "The employee already exists."
        except cls.DoesNotExist as e:
            employee = None

        branch = cls.objects.get(pk = data['pk_employee']).branch if data['pk_employee'] is not None else Branch.objects.get(pk = data['branch'])
        license = License.objects.get(branch=branch)
        validate = License.validate_date(branch)
        if validate['result']:
            if license.user > 0:
                if employee is None:
                    token = Token.objects.filter(key=data["token"]).first()
                    if token:
                        employee = cls(
                            type_worker_id = Type_Worker.objects.filter(id = data['type_worker_id']).first(),
                            sub_type_worker_id = Sub_Type_Worker.objects.filter(id = data['sub_type_worker_id']).first(),
                            payroll_type_document_identification_id = Payroll_Type_Document_Identification.objects.filter(id = data['payroll_type_document_identification_id']).first(),
                            municipality_id = Municipalities.objects.filter(id = data['municipality_id']).first(),
                            type_contract_id = Type_Contract.objects.filter(id = data['type_contract_id']).first(),
                            high_risk_pension = data['high_risk_pension'],
                            identification_number = data['identification_number'],
                            surname = data['surname'],
                            second_surname = data['second_surname'],
                            first_name = data['first_name'],
                            middle_name = None,
                            address = data['address'],
                            integral_salary = data['integral_salary'],
                            salary = data['salary'],
                            email = data['email'],
                            branch = branch,
                            user_name = data['user_name'].lower(),
                            psswd = get_random_string(length=20) if data['psswd'] is None else data['psswd'],
                            internal_email = f"{data['user_name'].lower()}@{branch.name.lower().replace(' ','_')}.com",
                            user_django = token.user
                        )
                        employee.save()
                        License.discount_user(branch)
                        result['code'] = 200
                        result['status'] = 'OK'
                        result['message'] = "Success"
                        for i in data['permissions']:
                            employee.permission.add(Permission.objects.get(pk = i))
                        _data = {"System":"Registration was carried out from the system"} if data['pk_employee'] is None else json.loads(cls.get_employee_serialized(data['pk_employee']).content.decode('utf-8'))[0]['fields']
                        History_Employee.register_movement("Created",_data,data)
            else:
                result['message'] = "Sorry, there are no more users"
        else:
            result['message'] = validate['message']
        return result

    @staticmethod
    def get_employee_serialized(employee_id):
        try:
            employee = Employee.objects.get(pk=employee_id)
            serialized_employee = serializers.serialize('json', [employee])
            return JsonResponse(json.loads(serialized_employee), safe=False)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Employee not found'}, status=404)

    @classmethod
    def get_list_employee(cls,data_):
        result = {
            "data": {},
            "code": 400,
            "status": "Fail",
            "message": "Token no valido"
        }
        data = []
        branch = Employee.objects.get(pk= data_['pk_employee']).branch
        try:
            for i in Employee.objects.filter(branch = branch):
                serialized_employee = serializers.serialize('json', [i])
                employee = json.loads(serialized_employee)[0]
                data.append(employee)
            result['code'] = 200
            result['status'] = 'OK'
            result['message'] = "Success"
        except Exception as e:
            result['message'] = str(e)
        result['data'] = data
        return result

    @classmethod
    def delete_user(cls, data):
        result = {
            "data": {},
            "code": 400,
            "status": "Fail",
            "message": "Token no valido"
        }
        try:
            employee = cls.objects.get(pk=data['pk_employee'])
            validate = License.validate_date(employee.branch)
            if validate['result']:
                License.add_user(employee.branch)
                employee.delete()
                result['code'] = 200
                result['status'] = 'OK'
                result['message'] = "Success"
            else:
                result['message'] = validate['message']
        except cls.DoesNotExist as e:
            employee = str(e)
        return result
        
    @classmethod
    def get_employee(cls, data):
        employee = Employee.objects.get(pk= data['pk_employee'])
        _e = json.loads(serializers.serialize('json', [employee]))[0]
        data = _e['fields']
        data['pk_employee'] = _e['pk']
        data['pk_municipalities'] =  Municipalities.objects.get(id = data['municipality_id'])._id
        data['name_municipalities'] =  Municipalities.objects.get(id = data['municipality_id']).name
        data['pk_Type_Worker'] =  Type_Worker.objects.get(id = data['municipality_id'])._id
        data['name_Type_Worker'] =  Type_Worker.objects.get(id = data['municipality_id']).name
        data['pk_Sub_Type_Worker'] =  Sub_Type_Worker.objects.get(id = data['municipality_id'])._id
        data['name_Sub_Type_Worker'] =  Sub_Type_Worker.objects.get(id = data['municipality_id']).name
        data['pk_Payroll_Type_Document_Identification'] =  Payroll_Type_Document_Identification.objects.get(id = data['municipality_id'])._id
        data['name_Payroll_Type_Document_Identification'] =  Payroll_Type_Document_Identification.objects.get(id = data['municipality_id']).name
        data['pk_Type_Contract'] =  Type_Contract.objects.get(id = data['municipality_id'])._id
        data['name_Type_Contract'] =  Type_Contract.objects.get(id = data['municipality_id']).name
        data['permission'] = [ {'pk_permission':i.pk,'name_permission':i.name} for i in employee.permission.all()]
        return data

class History_Employee(models.Model):
    ACTION_CHOICES = (
        ('Created', 'Created'),
        ('Modified', 'Modified'),
        ('Deleted', 'Deleted')
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, null = True, blank = True)
    user_who_registers = models.JSONField(null = True, blank = True)
    recorded_user = models.JSONField(null = True, blank = True)
    timestamp = models.DateTimeField(auto_now_add = True, null = True, blank = True)

    @classmethod
    def register_movement(cls,action,uwr, ru):
        cls(
            action = action,
            user_who_registers = uwr,
            recorded_user = ru
        ).save()



class Payment_Form_Employee(models.Model):
    payment_method = models.ForeignKey(Payment_Method, on_delete = models.CASCADE)
    bank_name = models.ForeignKey(BANK_NAME, on_delete = models.CASCADE,null=True,blank=True)
    account_type = models.CharField(max_length = 20,null=True,blank=True)
    account_number = models.IntegerField(null=True,blank=True)
    employee = models.ForeignKey(Employee, on_delete = models.CASCADE)

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.surname} - {self.payment_method.name} - {self.bank_name.name} - {self.account_type}"




























