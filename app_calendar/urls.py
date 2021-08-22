from django.urls import path
from .views import (CalendarView, FindCalendarView)

app_name = 'app_calendar'

urlpatterns = [
    path('calendar', CalendarView.as_view(), name='calendar_mgmt'),
    path('reverse', FindCalendarView.as_view(), name='reverse'),
]
