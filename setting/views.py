from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *


@api_view(["GET"])
def Get_Tax(request):
	return Response(Tax.get_list_tax())

@api_view(["GET"])
def Get_Unit_Measure(request):
	return Response(UnitMeasure.get_list_um())

@api_view(['GET'])
def Get_Type_Worker(request):
	return Response(Type_Worker.get_type_worker())

@api_view(['GET'])
def Get_Type_Contract(request):
	return Response(Type_Contract.get_type_contract())

@api_view(['GET'])
def Get_TSub_Type_Worker(request):
	return Response(Sub_Type_Worker.get_sub_type_worker())

@api_view(['GET'])
def Get_Payroll_Type_Document_Identification(request):
	return Response(Payroll_Type_Document_Identification.get_payroll_type_document_identification())

@api_view(['GET'])
def Get_CFDI(request):
	return Response(CFDI.get_list_cfdi())

@api_view(['GET'])
def Get_State(request):
	return Response(State.get_state())

@api_view(['GET'])
def Get_Municipalities(request):
	return Response(Municipalities.get_municipalities())

@api_view(['GET'])
def Get_Payment_Method(request):
	return Response(Payment_Method.get_list_payment_method())

@api_view(['GET'])
def Get_Payment_Form(request):
	return Response(Payment_Form.get_list_payment_form())

@api_view(['GET'])
def Get_Permission(request):
	return Response(Permission.get_list_permission())

@api_view(['GET'])
def Get_Type_Document_I(request):
	return Response(Type_Document_I.get_type_document_i())


@api_view(['GET'])
def Get_Type_Regimen(request):
	return Response(Type_Regimen.get_type_regimen())

@api_view(['GET'])
def Get_Type_Organization(request):
	return Response(Type_Organization.get_type_organization())

