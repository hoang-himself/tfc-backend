from django.urls import include, path
from . import views

urlpatterns = [
    # TODO
    path('list', views.list_class, name='list_classes'),
    path('<str:class_name>/list', views.list_user, name='list_class_users'),
]
