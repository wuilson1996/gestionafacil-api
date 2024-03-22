from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render
from .models import *

@api_view(['GET'])
def Report_Invoices(request):
	return Response(Report_Invoice.list_invoice(request.data))

@api_view(['GET'])
def Report_Invoice_Annulled(request):
	return Response(Report_Invoice.list_invoice_annulled(request.data))

@api_view(['GET'])
def Report_Inventorys(request):
	return Response(Report_Inventory.list_product(request.data))

@api_view(['GET'])
def Report_Product(request):
	return Response(Report_Inventory.report_product(request.data))

@api_view(['GET'])
def Get_Invoice_Shopping(request):
	return Response(Report_Shopping.get_invoice_shopping(request.data))

@api_view(['GET'])
def Close_The_Box_All(request):
	return Response(Report_Invoice.close_the_box_all(request.data))

@api_view(['GET'])
def History_Inventory(request):
	return Response(Hitory.history_inventory(request.data))

