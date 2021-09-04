from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView, TokenVerifyView)

from .views import AuthView

app_name = 'app_auth'

urlpatterns = [
    path(
        'login', csrf_exempt(TokenObtainPairView.as_view()), name='login'
    ),
    path('logout', AuthView.as_view(), name='logout'),
    path('refresh', TokenRefreshView.as_view(), name='refresh'),
    path('verify', TokenVerifyView.as_view(), name='verify'),
]
