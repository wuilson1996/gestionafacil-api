from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *

@api_view(['POST'])
def Create_Email(request):
	return Response(Emails.create_email(request.data))