from django.urls import path
from . import views

urlpatterns = [
    path('list', views.list_session, name='list'),
    path('create', views.create_session, name='add'),
    path('edit', views.edit_session, name='edit'),
    path('delete', views.delete_session, name='delete'),
    path('get', views.get_session, name='get'),
]
