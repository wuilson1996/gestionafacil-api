from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .up_cp import *
from threading import Thread

#Thread(target=up_cp).start()
#PostalCode.objects.all().delete()
#Thread(target=up_cp_excel).start()
#Municipalities.objects.all().delete()

#ClaveProdServ.objects.all().delete()
#Thread(target=download_prod_service).start()

@api_view(["GET"])
def Get_Tax(request):
	return Response(Tax.get_list_tax(request.data))

@api_view(["POST"])
def Create_Tax(request):
	return Response(Tax.create_tax(request.data))

@api_view(["DELETE"])
def Delete_Tax(request):
	return Response(Tax.delete_tax(request.data))


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
def Get_Clave_Prod_Serv(request):
	return Response(ClaveProdServ.get_list_clave_prod_serv())

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

@api_view(['GET'])
def Get_Sector(request):
	return Response(Sector.get_sector())

@api_view(['GET'])
def Get_TermPayment(request):
	return Response(TermPayment.get_list_term(request.data))

@api_view(['POST'])
def Create_TermPayment(request):
	return Response(TermPayment.create_term(request.data))

@api_view(['DELETE'])
def Delete_TermPayment(request):
	return Response(TermPayment.delete_term(request.data))

@api_view(['GET'])
def Get_TermAndCond(request):
	return Response(TermAndCond.get_term(request.data))

@api_view(['POST'])
def Create_TermAndCond(request):
	return Response(TermAndCond.create_term(request.data))

@api_view(['GET'])
def Get_Seller(request):
	return Response(SellerInfo.get_list_seller(request.data))

@api_view(['POST'])
def Create_Seller(request):
	return Response(SellerInfo.create_seller(request.data))

@api_view(['DELETE'])
def Delete_Seller(request):
	return Response(SellerInfo.delete_seller(request.data))

@api_view(['GET'])
def Get_Notification_Email(request):
	return Response(Notification.get_list_notification(request.data))

@api_view(['POST'])
def Create_Notification_Email(request):
	return Response(Notification.create_notification(request.data))

@api_view(['POST'])
def Change_Notification_Email(request):
	return Response(Notification.change_notification(request.data))

@api_view(["GET"])
def Get_Postal_Code(request):
	return Response(PostalCode.get_postal_code(request.GET["code"]))

@api_view(["GET"])
def Get_History(request):
	return Response(HistoryGeneral.get_history(request.data))

@api_view(["GET"])
def Get_List_Price(request):
	return Response(List_Price.get_list_price(request.data))

@api_view(["POST"])
def Create_List_Price(request):
	return Response(List_Price.create_price(request.data))

@api_view(["DELETE"])
def Delete_List_Price(request):
	return Response(List_Price.delete_list_price(request.data))

@api_view(["GET"])
def Get_MotivoCancel(request):
	return Response(MotivoCancel.get_list_motivo_cancel())