from django.conf.urls import url
from .views import *

urlpatterns=[
	url(r'^Save_Transfer/$',Save_Transfer,name="Save_Transfer"),
	url(r'^Return_Transfer/$',Return_Transfer,name="Return_Transfer"),
]