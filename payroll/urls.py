from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Create_Payroll/$',Create_Payroll,name="Create_Payroll"),
	url(r'^Get_List_Payroll/$',Get_List_Payroll,name="Get_List_Payroll"),
	url(r'^Basic_Payroll/$',Basic_Payroll,name="Basic_Payroll"),
	url(r'^Get_All_Payroll_Employee/$',Get_All_Payroll_Employee,name="Get_All_Payroll_Employee"),
	url(r'^Delete_Payroll/$',Delete_Payroll,name="Delete_Payroll"),
]