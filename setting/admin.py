from django.contrib import admin
from .models import *

class PostalCodeAdmin(admin.ModelAdmin):
    search_fields = ["id", "code"]

class StateAdmin(admin.ModelAdmin):
    search_fields = ["id", "name"]

class MunicipalitiesAdmin(admin.ModelAdmin):
    search_fields = ["id", "name"]

class ClaveProdServAdmin(admin.ModelAdmin):
    search_fields = ["code", "pk", "name"]

admin.site.register(Operation)
admin.site.register(BANK_NAME)
admin.site.register(Permission)

admin.site.register(State, StateAdmin)
admin.site.register(Municipalities, MunicipalitiesAdmin)
admin.site.register(Type_Document_I)
admin.site.register(Type_Document)
admin.site.register(Type_Organization)
admin.site.register(Type_Regimen)
admin.site.register(Transaction_Types)
admin.site.register(Book_Account)
admin.site.register(Book_Account_Type)

admin.site.register(Type_Contract)
admin.site.register(Payroll_Type_Document_Identification)
admin.site.register(Sub_Type_Worker)
admin.site.register(Type_Worker)

admin.site.register(Payment_Form)
admin.site.register(Payment_Method)
admin.site.register(CFDI)
admin.site.register(UnitMeasure)
admin.site.register(Tax)
admin.site.register(Sector)
admin.site.register(TermPayment)
admin.site.register(TermAndCond)
admin.site.register(Notification)
admin.site.register(PostalCode, PostalCodeAdmin)
admin.site.register(ClaveProdServ, ClaveProdServAdmin)
admin.site.register(HistoryGeneral)
admin.site.register(List_Price)
admin.site.register(MotivoCancel)
admin.site.register(EmailSMTP)
admin.site.register(MessageEmail)