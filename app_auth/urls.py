from django.urls import path
from .views import (login, logout, refresh)
from .views import (LoginView, LogoutView, RefreshView)
from django.views.decorators.csrf import (csrf_protect, ensure_csrf_cookie)

app_name = 'app_auth'

urlpatterns = [
    path('login', login, name='login'),
    path('logout', logout, name='logout'),
    path('refresh', refresh, name='refresh'),
]
