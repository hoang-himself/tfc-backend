from django.urls import path
from . import views


urlpatterns = [
    #TODO
    path('create', views.create_sched, name='create'),
    path('edit', views.edit_sched, name='edit'),
    path('delete', views.delete_sched, name='delete'),
    path('list', views.list_sched, name='list'),
    path('get', views.get_sched, name='get')
]
