from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Create_Email/$',Create_Email,name="Create_Email"),
	url(r'^Get_List_Emails/$',Get_List_Emails,name="Get_List_Emails"),
	url(r'^Get_List_Email_Sender/$',Get_List_Email_Sender,name="Get_List_Email_Sender"),
	url(r'^Is_Read/$',Is_Read,name="Is_Read"),
	url(r'^Get_Email/$',Get_Email,name="Get_Email"),
	url(r'^Mark_As_Read/$',Mark_As_Read,name="Mark_As_Read"),
]