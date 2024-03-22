from rest_framework.decorators import api_view
from rest_framework.response import Response
from invoice.models import Invoice
from user.models import Employee
from .models import Wallet

@api_view(['GET'])
def Get_List_Invoice_Credit(request):
	branch = Employee.objects.get(pk = request.data['pk_employee']).branch
	return Response(Invoice.get_list_invoice_credit(branch))

@api_view(['GET'])
def Get_Pass_Invoice(request):
	return Response(Wallet.get_pass_invoice(request.data))

@api_view(['GET'])
def Get_Pass_Shopping(request):
	return Response(Wallet.get_pass_shopping(request.data))

@api_view(['GET'])
def Get_All_History_Pass_Invoice(request):
	return Response(Wallet.get_all_history_pass_invoice(request.data))

@api_view(['GET'])
def Get_All_History_Pass_Customer(request):
	return Response(Wallet.get_all_history_pass_customer(request.data))