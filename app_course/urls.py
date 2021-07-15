from django.urls import path
from . import views

app_name = 'app_course'

urlpatterns = [
    path('get', views.get_course, name='get'),
    path('create', views.create_course, name='create'),
    path('list', views.list_course, name='list'),
    path('get-tags', views.get_tags, name='get-tags'),
    path('recommend-tags', views.recommend_tags, name='recommend-tags'),
    path('edit', views.edit_course, name='edit'),
    path('delete', views.delete_course, name='delete'),
]
