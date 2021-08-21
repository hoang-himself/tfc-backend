from django.urls import path
from .views import (SessionView, FindSessionView)

app_name = 'app_session'

urlpatterns = [
    # TODO Merge
    path('create', SessionView.as_view(), name='create'),
    path('get', SessionView.as_view(), name='get'),
    path('edit', SessionView.as_view(), name='edit'),
    path('delete', SessionView.as_view(), name='delete'),
    path('reverse', FindSessionView.as_view(), name='reverse'),
]
