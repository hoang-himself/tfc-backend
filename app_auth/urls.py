from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)


urlpatterns = [
    path('login', TokenObtainPairView.as_view(), name='login'),
    path('check', TokenVerifyView.as_view(), name='check'),
    path('logout', views.logout, name='logout'),
    path('refresh', TokenRefreshView.as_view(), name='refresh'),
]
