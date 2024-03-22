from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Report_Invoices/$',Report_Invoices,name="Report_Invoices"),
	url(r'^Report_Invoice_Annulled/$',Report_Invoice_Annulled,name="Report_Invoice_Annulled"),
	url(r'^Report_Inventory/$',Report_Inventorys,name="Report_Inventory"),
	url(r'^Report_Product/$',Report_Product,name="Report_Product"),
	url(r'^Get_Invoice_Shopping/$',Get_Invoice_Shopping,name="Get_Invoice_Shopping"),
	url(r'^Close_The_Box_All/$',Close_The_Box_All,name="Close_The_Box_All"),
	url(r'^History_Inventory/$',History_Inventory,name="History_Inventory"),
]