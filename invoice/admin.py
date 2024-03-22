from django.contrib import admin
from .models import *

admin.site.register(Invoice)
admin.site.register(Details_Invoice)
admin.site.register(Payment_Forms)
admin.site.register(Pass)
admin.site.register(History_Invoice)
admin.site.register(History_Pass)
admin.site.register(Note_Credit_Product)