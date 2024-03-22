from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer

@api_view(['POST'])
def Create_Customer(request):
	return Response(Customer.create_customer(request.data))


@api_view(['GET'])
def Get_List_Customer(request):
	return Response(Customer.get_list_customer(request.data))

@api_view(['GET'])
def Get_Customer(request):
	return Response(Customer.get_customer(request.data))

@api_view(['PUT'])
def Update_Customer(request):
	return Response(Customer.update_customer(request.data))

@api_view(['DELETE'])
def Delete_Client(request):
	return Response(Customer.delete_client(request.data))