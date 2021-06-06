from django.urls import include, path
from . import views

urlpatterns = [
    path('ping', views.ping, name='ping'),
    path('auth/', include('app_auth.urls')),
]