from user.models import Employee
from django.db import models
import json, base64, tempfile, env
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q
from django.core import serializers
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

class ReadStatus(models.Model):
    email = models.ForeignKey("Emails", on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    @classmethod
    def mark_as_read(cls, email, sender):
    	result = False
    	message = "I already read this email"
    	read_status, created = cls.objects.get_or_create(email=email, employee=sender)
    	if not read_status.is_read:
    		read_status.is_read = True
    		read_status.save()
    		result = True
    		message = "Email read"
    	print(message)
    	return {'result': result, 'message': message}

    @classmethod
    def mark_as_read_get(cls, data):
    	email = Emails.objects.get(pk = data['pk_email'])
    	employee = Employee.objects.get(pk = data['pk_employee'])
    	result = False
    	message = "I already read this email"
    	read_status, created = cls.objects.get_or_create(email = email, employee = employee)
    	if not read_status.is_read:
    		read_status.is_read = True
    		read_status.save()
    		result = True
    		message = "Email read"
    	print(message)
    	return {'result': result, 'message': message}

class Emails(models.Model):
	sender = models.ForeignKey(Employee, on_delete= models.CASCADE, related_name="envia")
	receives = models.ManyToManyField(Employee)
	subject = models.CharField(max_length= 255, null = True, blank= True)
	message = models.TextField()
	date_register = models.DateTimeField(auto_now_add= True, null = True, blank= True)

	def __str__(self):
		sender_name = f"From: {self.sender.first_name} {self.sender.surname}"
		receives_names = ", ".join([f"{receiver.first_name} {receiver.surname}" for receiver in self.receives.all()])
		subject = f"Subject: {self.subject}"
		date_register = f"Date: {self.date_register}"

		return f"{sender_name}\nTo: {receives_names}\n{subject}\n{date_register}\nMessage: {self.message[:50]}..."

	@classmethod
	def get_list_emails(cls, data):
	    result = False
	    message = None
	    _data = []
	    try:
	        employee = Employee.objects.get(pk=data['pk_employee'])
	        for email in cls.objects.filter(receives=employee).order_by('-date_register'):
	            _value = json.loads(serializers.serialize('json', [email]))[0]
	            _value['fields']['diferencia'] = cls.Calculate_Value(_value['fields']['date_register'])
	            _value['sender'] = {
	                'pk_employee': employee.pk,
	                'name': employee.first_name + ' ' + employee.surname,
	            }
	            read_status, created = ReadStatus.objects.get_or_create(email=email, employee=employee)
	            _value['is_read'] = read_status.is_read
	            files = []
	            try:
	            	for j in Attached_Files.objects.filter(email=email):
		                try:
		                    files.append({'url_files': f"{env.URL_LOCAL}{j.file.url}"})
		                except Exception as e:
		                    pass
	            except Attached_Files.DoesNotExist as e:
	            	pass
	            _value['files'] = files
	            _data.append(_value)

	        result = True
	        message = "Success"
	    except Exception as e:
	        message = str(e)
	    return {'result': result, 'message': message, 'data': _data}

	@classmethod
	def get_email(cls, data):
		email = cls.objects.get(pk = data['pk_email'])
		_data = json.loads( serializers.serialize('json', [email] ))[0]
		_data['fields']['diferencia'] = cls.Calculate_Value(_data['fields']['date_register'])
		_data['receives'] = [
			{
				"email":json.loads( serializers.serialize('json', [i] ))[0]['fields']['internal_email'],
				"name":f"{json.loads( serializers.serialize('json', [i] ))[0]['fields']['first_name']} {json.loads( serializers.serialize('json', [i] ))[0]['fields']['surname']}"
			}
			for i in email.receives.all()
		]
		try:
			file = Attached_Files.objects.get(email = email)
			url_file = f"{env.URL_LOCAL}{file.file.url}"
			print(file.file)
			file_content_base64 = base64.b64encode(file.file.read()).decode("utf-8")
			_data['file'] = {"url":url_file,'name':str(file.file)}
		except Exception as e:
			_data['file'] = {}
		
		return _data

	@staticmethod
	def Calculate_Value(Time):
		fecha_dada = datetime.strptime(Time, "%Y-%m-%dT%H:%M:%S.%f")
		fecha_dada = fecha_dada.replace(tzinfo=timezone.utc)
		fecha_actual = datetime.now(timezone.utc)
		diferencia = fecha_actual - fecha_dada
		diferencia -= timedelta(hours=5)
		diferencia_relativa = relativedelta(fecha_actual, fecha_dada)
		anos = diferencia_relativa.years
		meses = diferencia_relativa.months
		dias = diferencia.days
		segundos_totales = diferencia.seconds
		horas, segundos = divmod(segundos_totales, 3600)
		minutos, segundos = divmod(segundos, 60)

		message = None
		if anos > 0:
		    message = f"Hace {anos} {'año' if anos == 1 else 'años'}."
		elif meses > 0:
		    message = f"Hace {meses} {'mes' if meses == 1 else 'meses'}."
		elif dias > 0:
		    message = f"Hace {dias} {'día' if dias == 1 else 'días'}."
		elif horas > 0:
		    message = f"Hace {horas} {'hora' if horas == 1 else 'horas'}."
		elif minutos > 0:
		    message = f"Hace {minutos} {'minuto' if minutos == 1 else 'minutos'}."
		else:
		    message = "Hace menos de un minuto."
		return message

	@classmethod
	def is_read(cls, data):
		email = cls.objects.get(pk = data['pk_email'])
		email.is_read_email = data['is_read']
		email.save()
		return {'result':True}

	@classmethod
	def create_email(cls, data):
		result = False
		message = None
		try:
			sender = Employee.objects.get(pk = data['sender'])
			email = cls(
				sender = sender,
				subject = data['subject'],
				message = data['message']
			)
			email.save()
			for i in data['receives']:
				email.receives.add(Employee.objects.get(internal_email = i))
			read_status, created = ReadStatus.objects.get_or_create(email=email, employee=sender)
			ReadStatus.mark_as_read(email, sender)
			message = "Success"
			result = True
			print(data['file'])
			return Attached_Files.save_files(data['file'],email)
		except Exception as e:
			message = str(e)
			print(e,'ERROR EMAIL')
		return {'result':result, 'message':message}

	@classmethod
	def mark_as_read(cls, data):
	    email = cls.objects.get(pk=data['pk_email'])
	    receiver = Employee.objects.get(pk=data['pk_employee'])
	    read_status, created = ReadStatus.objects.get_or_create(email=email, employee=receiver)
	    if not read_status.is_read:
	        read_status.is_read = True
	        read_status.save()
	    return {'result': True}

	@classmethod
	def get_list_emails_sender(cls, data):
		result = False
		message = None
		_data = []
		try:
			employee = Employee.objects.get(pk=data['pk_employee'])
			for email in cls.objects.filter(sender=employee).order_by('-date_register'):
			    _value = json.loads(serializers.serialize('json', [email]))[0]
			    _value['fields']['diferencia'] = cls.Calculate_Value(_value['fields']['date_register'])
			    _value['sender'] = {
			        'pk_employee': employee.pk,
			        'name': employee.first_name + ' ' + employee.surname,
			    }
			    read_status, created = ReadStatus.objects.get_or_create(email=email, employee=employee)
			    _value['is_read'] = read_status.is_read
			    files = []
			    for j in Attached_Files.objects.filter(email=email):
			        files.append({
			            'url_files': f"{env.URL_LOCAL}{j.file.url}"
			        })
			    _value['files'] = files
			    _data.append(_value)
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return {'result':result, 'message':message, 'data':_data}

class Attached_Files(models.Model):
	email = models.ForeignKey(Emails, on_delete = models.CASCADE)
	file = models.FileField(upload_to= "files_emails")

	def __str__(self):
	    subject = self.email.subject
	    receives_names = ', '.join([f"{receiver.first_name} {receiver.surname}" for receiver in self.email.receives.all()])
	    sender_names = f"{self.email.sender.first_name} {self.email.sender.surname}"
	    branch_name = self.email.sender.branch.name
	    return f"{subject} - {receives_names} by {sender_names} ----- {branch_name}"
	    
	@classmethod
	def save_files(cls, data, email):
		result = False
		message = None
		try:
			file_data = base64.b64decode(data['base_64'])
			file_name = data['name_file']
			with tempfile.NamedTemporaryFile(delete=False) as temp_file:
			    temp_file.write(file_data)
			saved_file_path = default_storage.save(file_name, ContentFile(file_data))
			file_instance = cls(
			    email=email,
			    file=saved_file_path
			)
			file_instance.save()
			result = True
			message = "Success"
		except Exception as e:
		    message = str(e)
		    result = False
		    print(e,'ERROR FILES')
		return {'result': result, 'message': message}