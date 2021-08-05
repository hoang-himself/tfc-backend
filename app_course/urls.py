from django.urls import path
from .views import (CourseView, TagView, FindTagView, FindCourseView)

app_name = 'app_course'

urlpatterns = [
    # TODO Merge
    path('create', CourseView.as_view(), name='create'),
    path('get', CourseView.as_view(), name='get'),
    path('edit', CourseView.as_view(), name='edit'),
    path('delete', CourseView.as_view(), name='delete'),

    path('reverse', FindCourseView.as_view(), name='reverse'),

    path('tag/get', TagView.as_view(), name='get_tag'),
    path('tag/find', FindTagView.as_view(), name='find_tag'),
]
