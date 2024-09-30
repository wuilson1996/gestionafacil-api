from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Create_Company/$',Create_Company,name="Create_Company"),
	url(r'^Create_Resolution/$',Create_Resolution,name="Create_Resolution"),
	url(r'^Get_Resolution/$',Get_Resolution,name="Get_Resolution"),
	url(r'^Create_Branch/$',Create_Branch,name="Create_Branch"),
    url(r'^Delete_Branch/$',Delete_Branch,name="Delete_Branch"),
	url(r'^Update_Resolution/$',Update_Resolution,name="Update_Resolution"),
	url(r'^List_Branch/$',List_Branch,name="List_Branch"),
	url(r'^Update_Resolution_DIAN/$',Update_Resolution_DIAN,name="Update_Resolution_DIAN"),
	url(r'^Get_Branch/$',Get_Branch,name="Get_Branch"),
    url(r'^Get_Company/$',Get_Company,name="Get_Company"),
	url(r'^Get_Resolution_List/$',Get_Resolution_List,name="Get_Resolution_List"),
	url(r'^Update_Date_License/$',Update_Date_License,name="Update_Date_License"),
	url(r'^Change_Environment/$',Change_Environment,name="Change_Environment"),
	url(r'^Update_Branch/$',Update_Branch,name="Update_Branch"),
	url(r'^Update_Logo/$',Update_Logo,name="Update_Logo"),
    
	url(r'^Create_Store/$',Create_Store,name="Create_Store"),
    url(r'^Delete_Store/$',Delete_Store,name="Delete_Store"),
	url(r'^List_Store/$',List_Store,name="List_Store"),
	url(r'^Get_Store/$',Get_Store,name="Get_Store"),
    
	url(r'^Create_SerieFolio/$',Create_SerieFolio,name="Create_SerieFolio"),
    url(r'^Delete_SerieFolio/$',Delete_SerieFolio,name="Delete_SerieFolio"),
	url(r'^List_SerieFolio/$',List_SerieFolio,name="List_SerieFolio"),
    url(r'^Get_SerieFolio/$',Get_SerieFolio,name="Get_SerieFolio"),
    
	url(r'^Create_Consecutive/$',Create_Consecutive,name="Create_Consecutive"),
    url(r'^Get_Consecutive/$',Get_Consecutive,name="Get_Consecutive"),
    
	url(r'^Create_Bank/$',Create_Bank,name="Create_Bank"),
    url(r'^Delete_Bank/$',Delete_Bank,name="Delete_Bank"),
	url(r'^List_Bank/$',List_Bank,name="List_Bank"),
    url(r'^Get_Bank/$',Get_Bank,name="Get_Bank"),
]