from django.urls import path
from .views import (ClassView, ClassStudentView, FindClassView)

app_name = 'app_class'

urlpatterns = [
    # TODO Merge
    path('create', ClassView.as_view(), name='create'),
    path('get', ClassView.as_view(), name='get'),
    path('edit', ClassView.as_view(), name='edit'),
    path('delete', ClassView.as_view(), name='delete'),

    path('reverse', FindClassView.as_view(), name='reverse'),

    # TODO Merge
    path('add-student', ClassStudentView.as_view(), name='add_student'),
    path('delete-student', ClassStudentView.as_view(), name='delete_student'),
]
