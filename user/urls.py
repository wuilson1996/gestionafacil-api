from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Create_Employee/$',Create_Employee,name="Create_Employee"),
	url(r'^Login/$',Login,name="Login"),
    url(r'^Register/$',Register,name="Register"),
	url(r'^Get_List_Employee/$',Get_List_Employee,name="Get_List_Employee"),
	url(r'^Get_Employee/$',Get_Employee,name="Get_Employee"),
	url(r'^LogOut/$',LogOut,name="LogOut"),
	url(r'^Update_User/$',Update_User,name="Update_User"),
	url(r'^Delete_User/$',Delete_User,name="Delete_User"),
	url(r'^Query_Permissions/$',Query_Permissions,name="Query_Permissions"),
	url(r'^Get_List_Email/$',Get_List_Email,name="Get_List_Email"),
]