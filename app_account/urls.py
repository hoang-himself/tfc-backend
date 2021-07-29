from django.urls import path

from .views import (SelfView, UserView, StaffView)

app_name = 'app_account'

urlpatterns = [
    path('me', SelfView.as_view(), name='get-self'),

    path('list', UserView.as_view(), name='list-user'),
    path('create', UserView.as_view(), name='create-user'),
    path('edit', UserView.as_view(), name='edit-user'),
    path('delete', UserView.as_view(), name='delete-user'),

    path('staff/list', StaffView.as_view(), name='list-staff'),
    path('staff/create', StaffView.as_view(), name='create-staff'),
    path('staff/edit', StaffView.as_view(), name='edit-staff'),
    path('staff/delete', StaffView.as_view(), name='delete-staff'),
]
