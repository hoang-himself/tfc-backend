from django.urls import path
from . import views

app_name = 'app_account'

urlpatterns = [
    path('get', views.get_self, name='get-self'),

    path('list', views.list_user, name='list-user'),
    path('create', views.create_user, name='create-user'),
    path('edit', views.edit_user, name='edit-user'),
    path('delete', views.delete_user, name='delete-user'),

    path('staff/list', views.list_staff, name='list-staff'),
    path('staff/create', views.create_staff, name='create-staff'),
    path('staff/edit', views.edit_staff, name='edit-staff'),
    path('staff/delete', views.delete_staff, name='delete-staff'),
]
