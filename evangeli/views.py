from rest_framework.decorators import api_view
from rest_framework.response import Response
from invoice.models import Invoice
from django.db.models import Q

@api_view(['PUT'])
def Get_Invoice(request):
    return Response({'result':True})