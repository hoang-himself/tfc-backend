from django.urls import path

from .views import (SelfView, UserView, StaffView)

app_name = 'app_account'

urlpatterns = [
    path('me', SelfView.as_view(), name='get_self'),
    path('user', UserView.as_view(), name='user_mgmt'),
    path('staff', StaffView.as_view(), name='staff_mgmt'),
]
