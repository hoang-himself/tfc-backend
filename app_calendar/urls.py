from django.urls import path
from .views import (CalendarView, FindCalendarView)

app_name = 'app_calendar'

urlpatterns = [
    # TODO Merge
    path('create', CalendarView.as_view(), name='create'),
    path('get', CalendarView.as_view(), name='get'),
    path('edit', CalendarView.as_view(), name='edit'),
    path('delete', CalendarView.as_view(), name='delete'),

    path('reverse', FindCalendarView.as_view(), name='reverse'),
]
