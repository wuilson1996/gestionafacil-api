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
    url(r'^Delete_Invoice/$',Delete_Invoice,name="Delete_Invoice"),
    # Remission
    url(r'^Create_Remission/$',Create_Remission,name="Create_Remission"),
	url(r'^Get_List_Remission/$',Get_List_Remission,name="Get_List_Remission"),
	url(r'^Get_Remission/$',Get_Remission,name="Get_Remission"),
	url(r'^Delete_Remission/$',Delete_Remission,name="Delete_Remission"),
    
	# service
    url(r'^Create_Service/$',Create_Service,name="Create_Service"),
	url(r'^Get_List_Service/$',Get_List_Service,name="Get_List_Service"),
	url(r'^Get_Service/$',Get_Service,name="Get_Service"),
	url(r'^Delete_Service/$',Delete_Service,name="Delete_Service"),
    
	# cotization
    url(r'^Create_Cotization/$',Create_Cotization,name="Create_Cotization"),
	url(r'^Get_List_Cotization/$',Get_List_Cotization,name="Get_List_Cotization"),
	url(r'^Get_Cotization/$',Get_Cotization,name="Get_Cotization"),
	url(r'^Delete_Cotization/$',Delete_Cotization,name="Delete_Cotization"),
    
	# Order Buy
    url(r'^Create_Order_Buy/$',Create_Order_Buy,name="Create_Order_Buy"),
	url(r'^Get_List_Order_Buy/$',Get_List_Order_Buy,name="Get_List_Order_Buy"),
	url(r'^Get_Order_Buy/$',Get_Order_Buy,name="Get_Order_Buy"),
	url(r'^Delete_Order_Buy/$',Delete_Order_Buy,name="Delete_Order_Buy"),
    
	# invoice provider
    url(r'^Create_Invoice_Provider/$',Create_Invoice_Provider,name="Create_Invoice_Provider"),
	url(r'^Get_List_Invoice_Provider/$',Get_List_Invoice_Provider,name="Get_List_Invoice_Provider"),
	url(r'^Get_Invoice_Provider/$',Get_Invoice_Provider,name="Get_Invoice_Provider"),
	url(r'^Delete_Invoice_Provider/$',Delete_Invoice_Provider,name="Delete_Invoice_Provider"),
    
	# payment to provider
    url(r'^Create_Payment/$',Create_Payment,name="Create_Payment"),
	url(r'^Get_List_Payment/$',Get_List_Payment,name="Get_List_Payment"),
	url(r'^Get_Payment/$',Get_Payment,name="Get_Payment"),
	url(r'^Delete_Payment/$',Delete_Payment,name="Delete_Payment"),
    
	# payment to provider
    url(r'^Create_Payment_Invoice/$',Create_Payment_Invoice,name="Create_Payment_Invoice"),
	url(r'^Get_List_Payment_Invoice/$',Get_List_Payment_Invoice,name="Get_List_Payment_Invoice"),
	url(r'^Get_Payment_Invoice/$',Get_Payment_Invoice,name="Get_Payment_Invoice"),
	url(r'^Delete_Payment_Invoice/$',Delete_Payment_Invoice,name="Delete_Payment_Invoice"),
    
	# facturas frecuentes.
    url(r'^Create_Invoice_Frequent/$',Create_Invoice_Frequent,name="Create_Invoice_Frequent"),
	url(r'^Get_List_Invoice_Frequent/$',Get_List_Invoice_Frequent,name="Get_List_Invoice_Frequent"),
	url(r'^Get_Invoice_Frequent/$',Get_Invoice_Frequent,name="Get_Invoice_Frequent"),
	url(r'^Delete_Invoice_Frequent/$',Delete_Invoice_Frequent,name="Delete_Invoice_Frequent"),
	
	#history
	url(r'^Get_History/$',Get_History,name="Get_History"),

	# Finkok
	url(r'^Register_Client/$',Register_Client,name="Register_Client"),
    url(r'^Update_Register_Client/$',Update_Register_Client,name="Update_Register_Client"),
    url(r'^Get_Register_Client/$',Get_Register_Client,name="Get_Register_Client"),
    url(r'^Assign_Register_Client/$',Assign_Register_Client,name="Assign_Register_Client"),
    url(r'^StampXML/$',StampXML,name="StampXML"),
    url(r'^SingStampXML/$',SingStampXML,name="SingStampXML"),
    url(r'^SingStampPaymentXML/$',SingStampPaymentXML,name="SingStampPaymentXML"),
    url(r'^SingStampNC/$',SingStampNC,name="SingStampNC"),
    url(r'^GenerateXML/$',GenerateXML,name="GenerateXML"),
    url(r'^GenerateXMLPayment/$',GenerateXMLPayment,name="GenerateXMLPayment"),
    url(r'^GenerateXMLNC/$',GenerateXMLNC,name="GenerateXMLNC"),
    url(r'^SendEmail/$',SendEmail,name="SendEmail"),
]