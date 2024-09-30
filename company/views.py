from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.shortcuts import render
from .models import *


@api_view(['POST'])
def Create_Company(request):
	ip_address = request.META.get('REMOTE_ADDR', '')
	print(ip_address)
	return JsonResponse(Company.create_company(request.data))
 
@api_view(['POST'])
def Create_Branch(request):
	return JsonResponse(Branch.add_branch(request.data))
 
@api_view(['DELETE'])
def Delete_Branch(request):
	return JsonResponse(Branch.delete_branch(request.data))

@api_view(['PUT'])
def Update_Resolution(request):
	return JsonResponse(Resolution.update_resolution(request.data))

@api_view(['POST'])
def Create_Resolution(request):
	return JsonResponse(Resolution.create_resolution(request.data,Branch.objects.get(pk = request.data['pk_branch'])))	

@api_view(['GET'])
def Get_Resolution(request):
	return JsonResponse(Resolution.get_resolution(request.data))	

@api_view(['GET'])
def List_Branch(request):
	return Response(Branch.list_branch(request.data))	

@api_view(['PUT'])
def Update_Resolution_DIAN(request):
	return Response(Resolution.update_resolution_dian(request.data))

@api_view(['GET'])
def Get_Branch(request):
	return Response(Branch.get_branch(request.data))	

@api_view(['GET'])
def Get_Company(request):
	return Response(Company.get_company(request.data))	

@api_view(['GET'])
def Get_Resolution_List(request):
	return Response(Resolution.get_resolution_list(request.data))	

@api_view(['GET'])
def Update_Date_License(request):
	return Response(License.update_date_license(request.data))

@api_view(['PUT'])
def Change_Environment(request):
	return Response(Branch.change_environment(request.data))

@api_view(['PUT'])
def Update_Branch(request):
	return Response(Branch.update_branch(request.data))

@api_view(['PUT'])
def Update_Logo(request):
	return Response(Branch.update_logo(request.data))

# Store
@api_view(['POST'])
def Create_Store(request):
	return JsonResponse(Store.add_store(request.data))

@api_view(['GET'])
def List_Store(request):
	return JsonResponse(Store.list_store(request.data))

@api_view(['DELETE'])
def Delete_Store(request):
	return JsonResponse(Store.delete_store(request.data))

@api_view(['GET'])
def Get_Store(request):
	return JsonResponse(Store.get_store(request.data))

# Numbers
@api_view(['POST'])
def Create_SerieFolio(request):
	return JsonResponse(SerieFolio.create_serie_folio(request.data))

@api_view(['GET'])
def List_SerieFolio(request):
	return JsonResponse(SerieFolio.get_list_serie_folio(request.data))

@api_view(['DELETE'])
def Delete_SerieFolio(request):
	return JsonResponse(SerieFolio.delete_serie_folio(request.data))

@api_view(['GET'])
def Get_SerieFolio(request):
	return JsonResponse(SerieFolio.get_serie_folio(request.data))

# Consecutive
@api_view(['POST'])
def Create_Consecutive(request):
	return JsonResponse(Consecutive.create_consecutive(request.data))

@api_view(['GET'])
def Get_Consecutive(request):
	return JsonResponse(Consecutive.get_consecutive(request.data))

# Bank
@api_view(['POST'])
def Create_Bank(request):
	return JsonResponse(Bank.create_bank(request.data))

@api_view(['GET'])
def List_Bank(request):
	return JsonResponse(Bank.get_list_bank(request.data))

@api_view(['DELETE'])
def Delete_Bank(request):
	return JsonResponse(Bank.delete_bank(request.data))

@api_view(['GET'])
def Get_Bank(request):
	return JsonResponse(Bank.get_bank(request.data))