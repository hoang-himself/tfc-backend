from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import (LoginView, LogoutView, RefreshView)

app_name = 'app_auth'

urlpatterns = [
    path('login', csrf_exempt(LoginView.as_view()), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('refresh', RefreshView.as_view(), name='refresh'),
]
