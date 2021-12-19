from django.urls import re_path

from django_saml import views

app_name = 'django_saml'

urlpatterns = [
    re_path(r'metadata/?$', views.metadata, name='metadata'),
    re_path(r'acs/?$', views.saml_acs, name='acs'),
    re_path(r'login/?$', views.login, name='login'),
    re_path(r'logout/?$', views.logout, name='logout'),
    re_path(r'sls/?$', views.saml_sls, name='sls'),
]
