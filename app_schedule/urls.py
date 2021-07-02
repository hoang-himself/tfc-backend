from django.urls import path
from . import views


urlpatterns = [
    #TODO
    path('create', views.create_sched, name='create'),
    path('list', views.list_sched, name='list')
]
