from django.urls import path
from .views import (ScheduleView, FindScheduleView)

app_name = 'app_schedule'

urlpatterns = [
    path('schedule', ScheduleView.as_view(), name='schedule_mgmt'),
    path('reverse', FindScheduleView.as_view(), name='reverse'),
]
