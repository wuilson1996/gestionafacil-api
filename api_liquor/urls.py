from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^company/', include('company.urls')),
    url(r'^user/', include('user.urls')),
    url(r'^inventory/', include('inventory.urls')),
    url(r'^shopping/', include('shopping.urls')),
    url(r'^invoice/', include('invoice.urls')),
    url(r'^customer/', include('customer.urls')),
    url(r'^wallet/', include('wallet.urls')),
    url(r'^setting/', include('setting.urls')),
    url(r'^transfers/', include('transfers.urls')),
    url(r'^evangeli/', include('evangeli.urls')),
    url(r'^emails/', include('emails.urls')),
    url(r'^emails/', include('emails.urls')),
    url(r'^report/', include('report.urls')),
    url(r'^payroll/', include('payroll.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)