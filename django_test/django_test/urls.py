from django.urls import include, re_path
from django.contrib import admin

from sample import views

urlpatterns = [
    re_path(r'^saml/', include('django_saml.urls')),
    re_path(r'^admin/', admin.site.urls),
    re_path('^$', views.home),
    re_path(r'^logged-out/$', views.logged_out),
]
