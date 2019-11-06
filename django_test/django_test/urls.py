from django.contrib import admin
from django.urls import include, path

from sample import views

urlpatterns = [
    path('saml/', include('django_saml.urls')),
    path('admin/', admin.site.urls),
    path('', views.home),
    path('logged-out/', views.logged_out),
]
