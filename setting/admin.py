from django.contrib import admin
from .models import *

admin.site.register(Operation)
admin.site.register(BANK_NAME)
admin.site.register(Permission)

admin.site.register(State)
admin.site.register(Municipalities)
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