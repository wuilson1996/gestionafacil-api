from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Create_Invoice/$',Create_Invoice,name="Create_Invoice"),
	url(r'^Create_Pass_Invoice/$',Create_Pass_Invoice,name="Create_Pass_Invoice"),
	url(r'^Cancel_All_Invoice/$',Cancel_All_Invoice,name="Cancel_All_Invoice"),
	url(r'^Get_List_Invoice/$',Get_List_Invoice,name="Get_List_Invoice"),
	url(r'^Annulled_Invoice/$',Annulled_Invoice,name="Annulled_Invoice"),
	url(r'^Get_Invoice/$',Get_Invoice,name="Get_Invoice"),
	url(r'^Send_Invoice_DIAN/$',Send_Invoice_DIAN,name="Send_Invoice_DIAN"),
	url(r'^Get_Selling_By_Invoice/$',Get_Selling_By_Invoice,name="Get_Selling_By_Invoice"),
	url(r'^Get_Selling_By_Date/$',Get_Selling_By_Date,name="Get_Selling_By_Date"),
	url(r'^Generate_QR_Code_View/$',Generate_QR_Code_View,name="Generate_QR_Code_View"),
	url(r'^Annulled_Invoice_By_Product/$',Annulled_Invoice_By_Product,name="Annulled_Invoice_By_Product"),
]