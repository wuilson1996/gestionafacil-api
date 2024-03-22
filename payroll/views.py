from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *

@api_view(['POST'])
def Create_Payroll(request):
	return Response(Payroll.create_data_payroll(request.data))

@api_view(['GET'])
def Get_List_Payroll(request):
	return Response(Payroll.get_list_payroll(request.data))

@api_view(['POST'])
def Basic_Payroll(request):
	return Response(Payroll.basic_payroll(request.data))

@api_view(['GET'])
def Get_All_Payroll_Employee(request):
	return Response(Payroll.get_all_payroll_employee(request.data))

@api_view(['DELETE'])
def Delete_Payroll(request):
	return Response(Payroll.delete_payroll(request.data))