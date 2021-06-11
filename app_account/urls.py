from django.urls import path
from . import views

urlpatterns = [
    path('hello', views.hello_world, name='hello'),
    path('create', views.create_user, name='create'),
    path('list', views.viewUser, name='list'),
    path('email-check', views.emailCheck, name='email-check'),
    path('create-user', views.create_user, name='create')
]
