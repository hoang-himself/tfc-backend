from django.urls import path
from django.conf.urls import (
  handler400, handler403, handler404, handler500)
from . import views


urlpatterns = [
    #TODO
    path('create', views.create_sched, name='create'),
    path('edit', views.edit_sched, name='edit'),
    path('delete', views.delete_sched, name='delete'),
    path('list', views.list_sched, name='list')
]