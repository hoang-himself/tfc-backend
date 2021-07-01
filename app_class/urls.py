from django.urls import include, path
from . import views

urlpatterns = [
    # TODO
    path('list', views.list_class, name='list_classes'),
    path('create', views.create_class, name='create'),
    path('add-student', views.add_student, name='add-student'),
    path('delete-student', views.delete_student, name='delete-student'),
]
