from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Create_Shopping/$',Create_Shopping,name="Create_Shopping"),
	url(r'^Verified_Invoice/$',Verified_Invoice,name="Verified_Invoice"),
	url(r'^Create_Pass_Shopping/$',Create_Pass_Shopping,name="Create_Pass_Shopping"),
	url(r'^Cancel_All_Shopping/$',Cancel_All_Shopping,name="Cancel_All_Shopping"),
	url(r'^Get_Invoice_Shopping/$',Get_Invoice_Shopping,name="Get_Invoice_Shopping"),
]