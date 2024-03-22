from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Create_Company/$',Create_Company,name="Create_Company"),
	url(r'^Create_Resolution/$',Create_Resolution,name="Create_Resolution"),
	url(r'^Get_Resolution/$',Get_Resolution,name="Get_Resolution"),
	url(r'^Create_Branch/$',Create_Branch,name="Create_Branch"),
	url(r'^Update_Resolution/$',Update_Resolution,name="Update_Resolution"),
	url(r'^List_Branch/$',List_Branch,name="List_Branch"),
	url(r'^Update_Resolution_DIAN/$',Update_Resolution_DIAN,name="Update_Resolution_DIAN"),
	url(r'^Get_Branch/$',Get_Branch,name="Get_Branch"),
	url(r'^Get_Resolution_List/$',Get_Resolution_List,name="Get_Resolution_List"),
	url(r'^Update_Date_License/$',Update_Date_License,name="Update_Date_License"),
	url(r'^Change_Environment/$',Change_Environment,name="Change_Environment"),
	url(r'^Update_Branch/$',Update_Branch,name="Update_Branch"),
	url(r'^Update_Logo/$',Update_Logo,name="Update_Logo"),
]