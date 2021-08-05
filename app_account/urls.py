from django.urls import path

from .views import (SelfView, UserView, StaffView)

app_name = 'app_account'

urlpatterns = [
    path('me', SelfView.as_view(), name='get_self'),

    # TODO Merge
    path('create', UserView.as_view(), name='create_user'),
    path('get', UserView.as_view(), name='get_user'),
    path('edit', UserView.as_view(), name='edit_user'),
    path('delete', UserView.as_view(), name='delete_user'),

    # TODO merge
    path('staff/create', StaffView.as_view(), name='create_staff'),
    path('staff/get', StaffView.as_view(), name='get_staff'),
    path('staff/edit', StaffView.as_view(), name='edit_staff'),
    path('staff/delete', StaffView.as_view(), name='delete_staff'),
]
