from django.urls import path
from .views import (ScheduleView, FindScheduleView)

app_name = 'app_schedule'

urlpatterns = [
    #TODO Merge
    path('create', ScheduleView.as_view(), name='create'),
    path('get', ScheduleView.as_view(), name='get'),
    path('edit', ScheduleView.as_view(), name='edit'),
    path('delete', ScheduleView.as_view(), name='delete'),
    path('reverse', FindScheduleView.as_view(), name='reverse'),
]
