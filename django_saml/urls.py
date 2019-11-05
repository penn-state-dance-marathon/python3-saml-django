from django.urls import path

from django_saml import views

urlpatterns = [
    path('metadata', views.metadata, name='metadata'),
    path('acs', views.saml_acs, name='acs'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('sls', views.saml_sls, name='sls'),
]
