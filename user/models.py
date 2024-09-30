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
from invoice.app_email import *
from django.conf import settings

class Employee(models.Model):
    type_worker_id = models.ForeignKey(Type_Worker, on_delete = models.CASCADE, null = True, blank = True)
    sub_type_worker_id = models.ForeignKey(Sub_Type_Worker, on_delete = models.CASCADE, null = True, blank = True)
    payroll_type_document_identification_id = models.ForeignKey(Payroll_Type_Document_Identification, on_delete = models.CASCADE, null = True, blank = True)
    municipality_id = models.ForeignKey(Municipalities, on_delete = models.CASCADE, null = True, blank = True)
    type_contract_id = models.ForeignKey(Type_Contract, on_delete = models.CASCADE, null = True, blank = True)
    high_risk_pension = models.BooleanField(default = False)
    identification_number = models.CharField(max_length=150, blank=True, null=True)
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
    check_email = models.BooleanField(default = False)
    internal_email = models.EmailField(null=True, blank=True)
    user_django = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True)


    @classmethod
    def create_user_django(cls, data):
        result = {
            "code": 400,
            "status": "Fail",
            "message": "Usuario no disponible"
        }
        try:
            user = User.objects.filter(username=data["username"]).first()
            if not user:
                user = User.objects.create_user(username=data['username'], email=data['email'])
                user.set_password(data['psswd'])
                user.save()
                # create code verification email
                CheckUser.create_check_code(user)
                result["code"] = 200
                result["status"] = "OK"
                result["message"] = "Success"
        except Exception as e:
            result['message'] = str(e)
        return result


    @staticmethod
    def search_by_token(token):
        _token = Token.objects.get(key = token)
        _employee = Employee.objects.filter(user_django = _token.user)
        return _employee.first()
    
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
            # get or create code check email
            check_email_user = CheckUser.create_check_code(user)
            if check_email_user.check_email:
                employee = cls.objects.filter(user_django = user).first()
                if employee is not None:
                    #if employee.active:
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
                    #else:
                    #    result['message'] = "Su cuenta aun no ha sido activada."
                else:
                    result["data"] = {'token': str(token.key), "check": False}
                    result['code'] = 200
                    result['message'] = "Employee no ha sido configurado"
                    result['status'] = 'Employee'
            else:
                result['message'] = "Su cuenta aun no ha sido activada."
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
                    #employee.active = False
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
            employee = cls.objects.get(pk=data['pk_employee'])
            result['message'] = "The employee already exists."
        except cls.DoesNotExist as e:
            employee = None

        __employee = cls.objects.filter(pk = data['pk_employee']).first()
        branch = __employee.branch if __employee is not None else Branch.objects.get(pk = data['branch'])
        license = License.objects.get(branch=branch)
        validate = License.validate_date(branch)
        if not __employee:
            if validate['result']:
                if license.user > 0:
                    if employee is None:
                        token = Token.objects.filter(key = data["token"]).first()
                        if token:
                            _active = True
                            if data["state"] == "":
                                _active = False
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
                                email = data["email"] if "email" in data else token.user.email,
                                branch = branch,
                                user_name = data['user_name'].lower(),
                                psswd = get_random_string(length=20) if data['psswd'] is None else data['psswd'],
                                internal_email = f"{data['user_name'].lower()}@{branch.name.lower().replace(' ','_')}.com",
                                user_django = User.objects.filter(username=data["username"]).first() if data["username"] != None else token.user,
                                active = _active
                            )
                            employee.save()
                            License.discount_user(branch)
                            result['code'] = 200
                            result['status'] = 'OK'
                            result['message'] = "Success"
                            for i in data['permissions']:
                                employee.permission.add(Permission.objects.get(pk = int(i)))
                            data["pk_employee"] = employee.pk
                            #_data = {"System":"Registration was carried out from the system"} if data['pk_employee'] is None else json.loads(cls.get_employee_serialized(data['pk_employee']).content.decode('utf-8'))[0]['fields']
                            #History_Employee.register_movement("Created",_data,data)
                            if not data["username"]:
                                current_employee = Employee.search_by_token(token=data["token"])
                            else:
                                current_employee = employee
                            HistoryGeneral.create_history(
                                action=HistoryGeneral.CREATED,
                                class_models=HistoryGeneral.EMPLOYEE,
                                class_models_json=json.loads(cls.get_employee_serialized(data['pk_employee']).content.decode('utf-8'))[0],
                                employee=current_employee.pk,
                                username=current_employee.user_django.username,
                                branch=current_employee.branch.pk
                            )
                else:
                    result['message'] = "Sorry, there are no more users"
                    User.objects.filter(username=data["username"]).delete()
            else:
                result['message'] = validate['message']
        else:
            if Employee.check_by_token(token=data["token"]):
                current_employee = Employee.search_by_token(token=data["token"])
                if current_employee.branch.company == __employee.branch.company:
                    _active = True
                    if data["state"] == "":
                        _active = False
                    _user = __employee.user_django
                    _user.username = data["username"]
                    _user.email = data["email"]
                    if data["psswd"]:
                        _user.set_password(data["psswd"])
                    _user.save()

                    __employee.email = data["email"]
                    __employee.branch = Branch.objects.filter(pk = data['branch']).first()
                    __employee.first_name = data['first_name']
                    __employee.active = _active
                    for p in __employee.permission.all():
                        __employee.permission.remove(p)

                    for i in data['permissions']:
                        employee.permission.add(Permission.objects.get(pk = int(i)))

                    __employee.save()

                    #_data = {"System":"Registration was carried out from the system"} if data['pk_employee'] is None else json.loads(cls.get_employee_serialized(data['pk_employee']).content.decode('utf-8'))[0]['fields']
                    #History_Employee.register_movement("Update",_data,data)
                    HistoryGeneral.create_history(
                        action=HistoryGeneral.UPDATE,
                        class_models=HistoryGeneral.EMPLOYEE,
                        class_models_json=json.loads(cls.get_employee_serialized(data['pk_employee']).content.decode('utf-8'))[0],
                        employee=current_employee.pk,
                        username=current_employee.user_django.username,
                        branch=current_employee.branch.pk
                    )

                    result['code'] = 200
                    result['status'] = 'OK'
                    result['message'] = "Success"
                else:
                    result['message'] = "Insufficient permissions"
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
    def get_list_employee(cls, data):
        result = {
            "data": [],
            "code": 400,
            "status": "Fail",
            "message": "Token no valido"
        }
        
        try:
            if Employee.check_by_token(token=data["token"]):
                branch = Employee.search_by_token(token=data["token"]).branch
                company = branch.company
                for branch in Branch.objects.filter(company=company):
                    for i in Employee.objects.filter(branch = branch):
                        serialized_employee = serializers.serialize('json', [i])
                        employee = json.loads(serialized_employee)[0]
                        employee["fields"]["username"] = i.user_django.username
                        employee["fields"]["email"] = i.user_django.email
                        employee["fields"]["branch_name"] = i.branch.name
                        result['data'].append(employee)
                result['code'] = 200
                result['status'] = 'OK'
                result['message'] = "Success"
        except Exception as e:
            result['message'] = str(e)
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
            if Employee.check_by_token(token=data["token"]):
                __employee = Employee.search_by_token(token=data["token"])
                employee = cls.objects.get(pk=data['pk_employee'])
                validate = License.validate_date(employee.branch)
                if validate['result']:
                    License.add_user(employee.branch)
                    #employee.delete()
                    HistoryGeneral.create_history(
                        action=HistoryGeneral.DELETE,
                        class_models=HistoryGeneral.EMPLOYEE,
                        class_models_json=json.loads(cls.get_employee_serialized(data['pk_employee']).content.decode('utf-8'))[0],
                        employee=__employee.pk,
                        username=__employee.user_django.username,
                        branch=__employee.branch.pk
                    )
                    employee.user_django.delete()
                    result['code'] = 200
                    result['status'] = 'OK'
                    result['message'] = "Success"
                else:
                    result['message'] = validate['message']
        except cls.DoesNotExist as e:
            result['message'] = str(e)

        return result
        
    @classmethod
    def get_employee(cls, data):
        result = {
            "data": {},
            "code": 400,
            "status": "Fail",
            "message": "Token no valido"
        }
        try:
            if Employee.check_by_token(token=data["token"]):
                employee = Employee.search_by_token(token=data["token"])
                _e = json.loads(serializers.serialize('json', [employee]))[0]
                result["data"] = _e['fields']
                result["data"]['pk_employee'] = _e['pk']
                #result["data"]['pk_municipalities'] =  Municipalities.objects.filter(id = result["data"]['municipality_id']).first()._id
                #result["data"]['name_municipalities'] =  Municipalities.objects.filter(id = result["data"]['municipality_id']).first().name
                #result["data"]['pk_Type_Worker'] =  Type_Worker.objects.filter(id = result["data"]['municipality_id']).first()._id
                #result["data"]['name_Type_Worker'] =  Type_Worker.objects.filter(id = result["data"]['municipality_id']).first().name
                #result["data"]['pk_Sub_Type_Worker'] =  Sub_Type_Worker.objects.filter(id = result["data"]['municipality_id']).first()._id
                #result["data"]['name_Sub_Type_Worker'] =  Sub_Type_Worker.objects.filter(id = result["data"]['municipality_id']).first().name
                #result["data"]['pk_Payroll_Type_Document_Identification'] =  Payroll_Type_Document_Identification.objects.filter(id = result["data"]['municipality_id']).first()._id
                #result["data"]['name_Payroll_Type_Document_Identification'] =  Payroll_Type_Document_Identification.objects.filter(id = result["data"]['municipality_id']).first().name
                #result["data"]['pk_Type_Contract'] =  Type_Contract.objects.filter(id = result["data"]['municipality_id']).first()._id
                #result["data"]['name_Type_Contract'] =  Type_Contract.objects.filter(id = result["data"]['municipality_id']).first().name
                result["data"]['permission'] = [ {'pk_permission':i.pk,'name_permission':i.name} for i in employee.permission.all()]
                result['code'] = 200
                result["status"] = "OK"
                result["message"] = "Success"
        except cls.DoesNotExist as e:
            result['message'] = str(e)
        return result


class CheckUser(models.Model):
    code = models.CharField(max_length=100)
    check_email = models.BooleanField(default = False)
    created = models.DateTimeField()
    user = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True)
    
    def __str__(self) -> str:
        return str(self.code)+" - "+str(self.user)
    
    @classmethod
    def create_check_code(cls, user):
        check_email_user = cls.objects.filter(user=user).first()
        if not check_email_user:
            check_email_user = cls.objects.create(
                code = get_random_string(30),
                check_email = False,
                created = datetime.now(),
                user = user
            )
            cls.check_email_user(user)
        else:
            # verificar el tiempo de duracion del codigo
            pass
        
        return check_email_user
    
    @classmethod
    def check_email_user_with_code(cls, data):
        result = {
            "code": 400,
            "status": "Fail",
            "message": "Codigo no valido"
        }
        check_email_user = cls.objects.filter(user=User.objects.filter(username=data["username"]).first(), code=data["code"]).first()
        if check_email_user:
            check_email_user.check_email = True
            check_email_user.save()
            result["code"] = 200
            result["status"] = "OK"
            result["message"] = "Success"
        
        return result
    
    @classmethod
    def check_email_user(cls, user:User):
        check_email_user = cls.objects.filter(user=user).first()
        email_smtp = EmailSMTP.objects.all().last()
        email_send = MessageEmail.objects.filter(type_message=MessageEmail.CHECK_EMAIL).first()
        send(
            email_smtp.email,
            email_smtp.password,
            ""+user.email,
            email_send.asunto,
            "",
            email_send.message+" "+str(settings.URL_SITE)+"/check-user?code="+str(check_email_user.code)+"&username="+str(user.username),
            "",
            email_smtp.host,
            email_smtp.port
        )

    @classmethod
    def get_check_user(cls, user):
        return cls.objects.filter(user=user).first()


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




























