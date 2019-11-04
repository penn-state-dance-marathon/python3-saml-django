from django.urls import path

from django_saml import views

urlpatterns = [
    path('metadata', views.metadata),
    path('acs', views.saml_acs),
    path('login', views.login),
]
