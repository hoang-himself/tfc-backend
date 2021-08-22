from django.urls import path
from .views import (ClassView, ClassStudentView, FindClassView)

app_name = 'app_class'

urlpatterns = [
    path('class', ClassView.as_view(), name='class_mgmt'),
    path('reverse', FindClassView.as_view(), name='reverse'),
    path('student', ClassStudentView.as_view(), name='student_mgmt'),
]
