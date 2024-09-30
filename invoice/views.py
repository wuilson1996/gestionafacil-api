from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .finkok import *

@api_view(['POST'])
def Create_Invoice(request):
	return Response(Invoice.create_invoice(request.data))


@api_view(['POST'])
def Create_Pass_Invoice(request):
	return Response(Pass.create_pass(request.data))

@api_view(['POST'])
def Cancel_All_Invoice(request):
	return Response(Pass.cancel_all_invoices(request.data))

@api_view(['POST'])
def Annulled_Invoice_By_Product(request):
	return Response(Invoice.annulled_invoice_by_product(request.data))

@api_view(['GET'])
def Get_List_Invoice(request):
	return Response(Invoice.get_list_invoice(request.data))	

@api_view(['POST'])
def Annulled_Invoice(request):
	return Response(Invoice.annulled_invoice(request.data))	

@api_view(['GET'])
def Get_Invoice(request):
	return Response(Invoice.get_invoice(request.data))

@api_view(['GET'])
def Get_Selling_By_Invoice(request):
	return Response(Invoice.get_selling_by_invoice(request.data))

@api_view(['POST'])
def Send_Invoice_DIAN(request):
	return Response(Invoice.send_invoice_dian(request.data))

@api_view(['GET'])
def Get_Selling_By_Date(request):
	return Response(Invoice.get_selling_by_date(request.data))

@api_view(['POST'])
def Generate_QR_Code_View(request):
	return Response(Invoice.generate_qr_code_view(request.data))

@api_view(["POST"])
def Delete_Invoice(request):
	#return Response(Invoice.delete_invoice(request.data))
	finkok = FinkokService()
	result = finkok.sign_cancel(request.data)
	print(type(result))
	return Response(result)

# remission
@api_view(['POST'])
def Create_Remission(request):
	return Response(Remission.create_remission(request.data))

@api_view(['GET'])
def Get_List_Remission(request):
	return Response(Remission.get_list_remission(request.data))

@api_view(['GET'])
def Get_Remission(request):
	return Response(Remission.get_remission(request.data))

@api_view(["POST"])
def Delete_Remission(request):
	return Response(Remission.delete_remission(request.data))


# service
@api_view(['POST'])
def Create_Service(request):
	return Response(Service.create_service(request.data))

@api_view(['GET'])
def Get_List_Service(request):
	return Response(Service.get_list_service(request.data))

@api_view(['GET'])
def Get_Service(request):
	return Response(Service.get_service(request.data))

@api_view(["POST"])
def Delete_Service(request):
	return Response(Service.delete_service(request.data))


# cotization
@api_view(['POST'])
def Create_Cotization(request):
	return Response(Cotization.create_cotization(request.data))

@api_view(['GET'])
def Get_List_Cotization(request):
	return Response(Cotization.get_list_cotization(request.data))

@api_view(['GET'])
def Get_Cotization(request):
	return Response(Cotization.get_cotization(request.data))

@api_view(["POST"])
def Delete_Cotization(request):
	return Response(Cotization.delete_cotization(request.data))

# order buy
@api_view(['POST'])
def Create_Order_Buy(request):
	return Response(OrderBuy.create_order_buy(request.data))

@api_view(['GET'])
def Get_List_Order_Buy(request):
	return Response(OrderBuy.get_list_order_buy(request.data))

@api_view(['GET'])
def Get_Order_Buy(request):
	return Response(OrderBuy.get_order_buy(request.data))

@api_view(["POST"])
def Delete_Order_Buy(request):
	return Response(OrderBuy.delete_order_buy(request.data))

# invoice provider
@api_view(['POST'])
def Create_Invoice_Provider(request):
	return Response(InvoiceProvider.create_invoice_provider(request.data))

@api_view(['GET'])
def Get_List_Invoice_Provider(request):
	return Response(InvoiceProvider.get_list_invoice_provider(request.data))

@api_view(['GET'])
def Get_Invoice_Provider(request):
	return Response(InvoiceProvider.get_invoice_provider(request.data))

@api_view(["POST"])
def Delete_Invoice_Provider(request):
	return Response(InvoiceProvider.delete_invoice_provider(request.data))

# payment invoice provider
@api_view(['POST'])
def Create_Payment(request):
	return Response(PaymentInvoiceProvider.create_payment(request.data))

@api_view(['GET'])
def Get_List_Payment(request):
	return Response(PaymentInvoiceProvider.get_list_payment(request.data))

@api_view(['GET'])
def Get_Payment(request):
	return Response(PaymentInvoiceProvider.get_payment(request.data))

@api_view(["POST"])
def Delete_Payment(request):
	return Response(PaymentInvoiceProvider.delete_payment(request.data))


@api_view(["GET"])
def Get_History(request):
	return Response(History_Invoice.get_history(request.data))

# payment invoice
@api_view(['POST'])
def Create_Payment_Invoice(request):
	return Response(PaymentInvoice.create_payment(request.data))

@api_view(['GET'])
def Get_List_Payment_Invoice(request):
	return Response(PaymentInvoice.get_list_payment(request.data))

@api_view(['GET'])
def Get_Payment_Invoice(request):
	return Response(PaymentInvoice.get_payment(request.data))

@api_view(["POST"])
def Delete_Payment_Invoice(request):
	return Response(PaymentInvoice.delete_payment(request.data))

# invoice frequent
@api_view(['POST'])
def Create_Invoice_Frequent(request):
	return Response(InvoiceFrequent.create_invoice_frequent(request.data))

@api_view(['GET'])
def Get_List_Invoice_Frequent(request):
	return Response(InvoiceFrequent.get_list_invoice_frequent(request.data))

@api_view(['GET'])
def Get_Invoice_Frequent(request):
	return Response(InvoiceFrequent.get_invoice_frequent(request.data))

@api_view(["POST"])
def Delete_Invoice_Frequent(request):
	return Response(InvoiceFrequent.delete_invoice_frequent(request.data))


@api_view(["GET"])
def Get_History(request):
	return Response(History_Invoice.get_history(request.data))

@api_view(["POST"])
def Register_Client(request):
	finkok = FinkokService(request.data["rfc"])
	result = finkok.register_client()
	print(type(result))

	return Response(result)

@api_view(["POST"])
def Update_Register_Client(request):
	finkok = FinkokService(request.data["rfc"])
	result = finkok.update_register_client(request.data["status"])
	print(type(result))

	return Response(result)

@api_view(["POST"])
def Get_Register_Client(request):
	finkok = FinkokService(request.data["rfc"])
	result = finkok.get_register_client()
	print(type(result))

	return Response(result)

@api_view(["POST"])
def Assign_Register_Client(request):
	finkok = FinkokService(request.data["rfc"])
	result = finkok.assign_register_client(request.data["credit"])
	print(type(result))

	return Response(result)

@api_view(["POST"])
def StampXML(request):
	finkok = FinkokService()
	result = finkok.stamp()
	print(type(result))

	return Response(result)

@api_view(["POST"])
def SingStampXML(request):
	finkok = FinkokService()
	result = finkok.sing_stamp(request.data)
	print(type(result))

	return Response(result)

@api_view(["POST"])
def SingStampPaymentXML(request):
	finkok = FinkokService()
	result = finkok.sing_stamp_payment(request.data)
	print(type(result))

	return Response(result)

@api_view(["POST"])
def SingStampNC(request):
	finkok = FinkokService()
	result = finkok.sing_stamp_credit_note(request.data)
	print(type(result))

	return Response(result)

@api_view(["POST"])
def GenerateXML(request):
	finkok = FinkokService()
	result = finkok.generate_xml(request.data)
	print(type(result))

	return Response(result)

@api_view(["POST"])
def GenerateXMLPayment(request):
	finkok = FinkokService()
	result = finkok.generate_payment_xml(request.data)
	print(type(result))

	return Response(result)

@api_view(["POST"])
def GenerateXMLNC(request):
	finkok = FinkokService()
	result = finkok.generate_xml_nc(request.data)
	print(type(result))

	return Response(result)

@api_view(["POST"])
def SendEmail(request):
	if request.data["option"] == "invoice":
		invoice = Invoice()
		result = invoice.send_email(request.data)
	elif request.data["option"] == "remission":
		remission = Remission()
		result = remission.send_email(request.data)
	elif request.data["option"] == "service":
		service = Service()
		result = service.send_email(request.data)
	elif request.data["option"] == "cotization":
		cotization = Cotization()
		result = cotization.send_email(request.data)
	else:
		result = {
			"message": "Option not valid",
			"status": "Fail",
			"code": 400
		}
	return Response(result)