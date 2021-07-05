from django.urls import include, path
from . import views

urlpatterns = [
    path('ping', views.ping, name='ping'),
    # path('account/', include('app_account.urls')),
    # path('attend/', include('app_attend.urls')),
    path('auth/', include('app_auth.urls')),
    # path('calendar/', include('app_calendar.urls')),
    # path('class/', include('app_class.urls')),
    # path('course/', include('app_course.urls')),
    # path('log/', include('app_log.urls')),
    # path('role/', include('app_role.urls')),
    # path('schedule/', include('app_schedule.urls')),
]
