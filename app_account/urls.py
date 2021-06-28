from django.urls import path
from . import views

urlpatterns = [
    path('list', views.list_user, name='list'),
    path('create', views.create_user, name='create'),
]
