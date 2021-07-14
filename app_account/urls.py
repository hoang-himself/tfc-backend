from django.urls import path
from . import views

app_name = 'app_account'

urlpatterns = [
    path('get', views.get_self, name='get_self'),

    path('list', views.list_user, name='list_user'),
    path('create', views.create_user, name='create_user'),
    path('edit', views.edit_user, name='edit_user'),
    path('delete', views.delete_user, name='delete_user'),

    path('staff/list', views.list_staff, name='list_staff'),
    path('staff/create', views.create_staff, name='create_staff'),
    path('staff/edit', views.edit_staff, name='edit_staff'),
    path('staff/delete', views.delete_staff, name='delete_staff'),
]
