from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Report_Invoices/$',Report_Invoices,name="Report_Invoices"),
    url(r'^Report_Invoices_by_item/$',Report_Invoices_by_item,name="Report_Invoices_by_item"),
    url(r'^Report_Invoices_by_client/$',Report_Invoices_by_client,name="Report_Invoices_by_client"),
    url(r'^Report_Invoices_by_seller/$',Report_Invoices_by_seller,name="Report_Invoices_by_seller"),
    url(r'^Report_Invoices_by_item_profit/$',Report_Invoices_by_item_profit,name="Report_Invoices_by_item_profit"),
    url(r'^Report_State_Account/$',Report_Invoices_by_account,name="Report_State_Account"),
    
	url(r'^Report_Invoice_Annulled/$',Report_Invoice_Annulled,name="Report_Invoice_Annulled"),
	url(r'^Report_Inventory/$',Report_Inventorys,name="Report_Inventory"),
	url(r'^Report_Product/$',Report_Product,name="Report_Product"),
	url(r'^Get_Invoice_Shopping/$',Get_Invoice_Shopping,name="Get_Invoice_Shopping"),
	url(r'^Close_The_Box_All/$',Close_The_Box_All,name="Close_The_Box_All"),
	url(r'^History_Inventory/$',History_Inventory,name="History_Inventory"),
]