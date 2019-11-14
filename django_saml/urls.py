from django.conf.urls import url

from django_saml import views

app_name = 'django_saml'

urlpatterns = [
    url(r'metadata/?$', views.metadata, name='metadata'),
    url(r'acs/?$', views.saml_acs, name='acs'),
    url(r'login/?$', views.login, name='login'),
    url(r'logout/?$', views.logout, name='logout'),
    url(r'sls/?$', views.saml_sls, name='sls'),
]
