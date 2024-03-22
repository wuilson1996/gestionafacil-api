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