from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('check', views.check, name='check'),
    path('logout', views.logout, name='logout'),
    path('refresh', views.refresh, name='refresh'),
]
