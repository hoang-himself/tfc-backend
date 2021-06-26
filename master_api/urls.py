from django.urls import include, path
from . import views

urlpatterns = [
    path('ping', views.ping, name='ping'),
    path('auth/', include('app_auth.urls')),
    path('account/', include('app_account.urls')),
    path('calendar/', include('app_calendar.urls')),
    path('class/', include('app_class.urls')),
    path('role/', include('app_role.urls')),
]
