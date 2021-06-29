from django.urls import path
from . import views


urlpatterns = [
    #TODO
    path('create', views.create_course, name='create'),
    path('list', views.list_course, name='list')
]
