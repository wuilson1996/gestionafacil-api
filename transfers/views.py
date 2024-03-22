from rest_framework.response import Response
from .models import *
from rest_framework.decorators import api_view

@api_view(['POST'])
def Save_Transfer(request):
	return Response(Transfer.transfer_products(request.data))

@api_view(['PUT'])
def Return_Transfer(request):
	return Response(Transfer.return_transfer(request.data))