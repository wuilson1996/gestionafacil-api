from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *

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
	return Response(Invoice.get_invoice(request.data['pk_invoice']))

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