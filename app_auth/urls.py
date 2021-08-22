from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import (AuthView, RefreshView)

app_name = 'app_auth'

urlpatterns = [
    path('login', csrf_exempt(AuthView.as_view()), name='login'),
    path('logout', AuthView.as_view(), name='logout'),
    path('refresh', RefreshView.as_view(), name='refresh'),
]
