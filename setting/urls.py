from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Get_Type_Worker/$',Get_Type_Worker,name="Get_Type_Worker"),
	url(r'^Get_Type_Contract/$',Get_Type_Contract,name="Get_Type_Contract"),
	url(r'^Get_TSub_Type_Worker/$',Get_TSub_Type_Worker,name="Get_TSub_Type_Worker"),
	url(r'^Get_Payroll_Type_Document_Identification/$',Get_Payroll_Type_Document_Identification,name="Get_Payroll_Type_Document_Identification"),
    url(r'^Get_State/$',Get_State,name="Get_State"),
    url(r'^Get_CFDI/$',Get_CFDI,name="Get_CFDI"),
    url(r'^Get_Payment_Method/$',Get_Payment_Method,name="Get_Payment_Method"),
    url(r'^Get_Payment_Form/$',Get_Payment_Form,name="Get_Payment_Form"),
	url(r'^Get_Municipalities/$',Get_Municipalities,name="Get_Municipalities"),
	url(r'^Get_Permission/$',Get_Permission,name="Get_Permission"),
	url(r'^Get_Type_Document_I/$',Get_Type_Document_I,name="Get_Type_Document_I"),
	url(r'^Get_Type_Regimen/$',Get_Type_Regimen,name="Get_Type_Regimen"),
	url(r'^Get_Type_Organization/$',Get_Type_Organization,name="Get_Type_Organization"),
    url(r'^Get_Unit_Measure/$',Get_Unit_Measure,name="Get_Unit_Measure"),
    url(r'^Get_Tax/$',Get_Tax,name="Get_Tax"),
]