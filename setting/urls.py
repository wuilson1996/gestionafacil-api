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
    url(r'^Create_Tax/$',Create_Tax,name="Create_Tax"),
    url(r'^Delete_Tax/$',Delete_Tax,name="Delete_Tax"),
    url(r'^Get_Sector/$',Get_Sector,name="Get_Sector"),
    url(r'^Get_TermPayment/$',Get_TermPayment,name="Get_TermPayment"),
    url(r'^Create_TermPayment/$',Create_TermPayment,name="Create_TermPayment"),
    url(r'^Delete_TermPayment/$',Delete_TermPayment,name="Delete_TermPayment"),
    url(r'^Get_TermAndCond/$',Get_TermAndCond,name="Get_TermAndCond"),
    url(r'^Create_TermAndCond/$',Create_TermAndCond,name="Create_TermAndCond"),
    url(r'^Get_Seller/$',Get_Seller,name="Get_Seller"),
    url(r'^Create_Seller/$',Create_Seller,name="Create_Seller"),
    url(r'^Delete_Seller/$',Delete_Seller,name="Delete_Seller"),
    url(r'^Get_Notification_Email/$',Get_Notification_Email,name="Get_Notification_Email"),
    url(r'^Create_Notification_Email/$',Create_Notification_Email,name="Create_Notification_Email"),
    url(r'^Change_Notification_Email/$',Change_Notification_Email,name="Change_Notification_Email"),
    url(r'^Get_Postal_Code/$',Get_Postal_Code,name="Get_Postal_Code"),
    url(r'^Get_Clave_Prod_Serv/$',Get_Clave_Prod_Serv,name="Get_Clave_Prod_Serv"),

    #history
	url(r'^Get_History/$',Get_History,name="Get_History"),

    url(r'^Get_List_Price/$',Get_List_Price,name="Get_List_Price"),
    url(r'^Create_List_Price/$',Create_List_Price,name="Create_List_Price"),
    url(r'^Delete_List_Price/$',Delete_List_Price,name="Delete_List_Price"),

    url(r'^Get_MotivoCancel/$',Get_MotivoCancel,name="Get_MotivoCancel"),
]