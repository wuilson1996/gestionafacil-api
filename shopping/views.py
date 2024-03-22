from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import *

@api_view(['POST'])
def Create_Shopping(request):
	return Response(Shopping.create_shopping(request.data))

@api_view(['GET'])
def Verified_Invoice(request):
	return Response(Shopping.verified_invoice(request.data))	

@api_view(['POST'])
def Create_Pass_Shopping(request):
	return Response(Pass.create_pass(request.data))

@api_view(['POST'])
def Cancel_All_Shopping(request):
	return Response(Pass.cancel_all_invoices(request.data))

@api_view(['GET'])
def Get_Invoice_Shopping(request):
	return Response(Shopping.get_invoice_shopping(request.data))