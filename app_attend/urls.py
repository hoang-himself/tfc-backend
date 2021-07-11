from django.urls import path
from . import views

urlpatterns = [
    path('list', views.list_attend, name='list'),
    path('add', views.add_attend, name='add'),
    path('edit', views.edit_attend, name='edit'),
]