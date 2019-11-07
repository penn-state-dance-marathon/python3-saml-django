from django.conf.urls import include, url
from django.contrib import admin

from sample import views

urlpatterns = [
    url(r'^saml/', include('django_saml.urls')),
    url(r'^admin/', admin.site.urls),
    url('^$', views.home),
    url(r'^logged-out/$', views.logged_out),
]
