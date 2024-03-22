from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Get_Invoice/$',Get_Invoice,name="Get_Invoice"),
]