from django.contrib import admin
from django.conf.urls import url, include

from sample import views

urlpatterns = [
    url(r'^saml/', include('django_saml.urls')),
    url(r'^admin/', admin.site.urls),
    url('^$', views.home),
    url(r'^logged-out/$', views.logged_out),
]
