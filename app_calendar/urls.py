from django.urls import path
from . import views


urlpatterns = [
    #TODO
    path('list', views.list_calendar, name='list'),
]
