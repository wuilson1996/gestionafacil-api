from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Employee, CheckUser

@api_view(['POST'])
def Create_Employee(request):
	return Response(Employee.create_employee(request.data))

@api_view(['POST'])
def Login(request):
	return Response(Employee.login(request.data))

@api_view(['POST'])
def Register(request):
	return Response(Employee.create_user_django(request.data))

@api_view(['GET'])
def Get_List_Employee(request):
	return Response(Employee.get_list_employee(request.data))

@api_view(['GET'])
def Get_Employee(request):
	return Response(Employee.get_employee(request.data))


@api_view(['POST'])
def LogOut(request):
	return Response(Employee.logout(request.data))

@api_view(['PUT'])
def Update_User(request):
	return Response(Employee.Update_User(request.data))

@api_view(['DELETE'])
def Delete_User(request):
	return Response(Employee.delete_user(request.data))

@api_view(['GET'])
def Query_Permissions(request):
	return Response(Employee.query_permissions(request.data))

@api_view(['GET'])
def Get_List_Email(request):
	return Response(Employee.get_list_email(request.data))

@api_view(['POST'])
def Check_Email_User_With_Code(request):
	return Response(CheckUser.check_email_user_with_code(request.data))