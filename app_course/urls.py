from django.urls import path
from . import views


urlpatterns = [
    #TODO
    path('create', views.create_course, name='create'),
    path('list', views.list_course, name='list'),
    path('get-tags', views.get_tags, name='get-tags'),
    path('recommend-tags', views.recommend_tags, name='recommend-tags'),
    path('edit', views.edit_course, name='eidt'),
    path('delete', views.delete_course, name='delete'),
]
