from django.urls import path
from .views import (CourseView, TagView, FindTagView, FindCourseView)

app_name = 'app_course'

urlpatterns = [
    path('course', CourseView.as_view(), name='course_mgmt'),
    path('reverse', FindCourseView.as_view(), name='reverse'),

    # TODO Name implies similar functionality
    path('tag/get', TagView.as_view(), name='get_tag'),
    path('tag/find', FindTagView.as_view(), name='find_tag'),
]
