from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *

@api_view(['POST'])
def Create_Email(request):
	return Response(Emails.create_email(request.data))

@api_view(['GET'])
def Get_List_Emails(request):
	return Response(Emails.get_list_emails(request.data))

@api_view(['PUT'])
def Is_Read(request):
	return Response(Emails.is_read(request.data))


@api_view(['GET'])
def Get_List_Email_Sender(request):
	return Response(Emails.get_list_emails_sender(request.data))

@api_view(['GET'])
def Get_Email(request):
	return Response(Emails.get_email(request.data))


@api_view(['PUT'])
def Mark_As_Read(request):
	print(request.data)
	return Response(ReadStatus.mark_as_read_get(request.data))

