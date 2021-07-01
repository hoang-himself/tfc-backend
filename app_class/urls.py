from django.urls import include, path
from . import views

urlpatterns = [
    # TODO
    path('list', views.list_class, name='list_classes'),
    path('create', views.create_class, name='create'),
]
