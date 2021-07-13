from django.urls import path
from . import views

urlpatterns = [
    path('list', views.list_session, name='list'),
    path('add', views.add_session, name='add'),
    path('edit', views.edit_session, name='edit'),
]