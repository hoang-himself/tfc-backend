from django.urls import include, path
from . import views

urlpatterns = [
    path('test', views.test, name='test-connection'),
    path('login', views.login, name='login'),
    # path('teacher-check', views.teacher_check, name='teacher-check')
]
