from django.urls import path
from . import views

urlpatterns = [
    path('create', views.create_user, name='create'),
    path('list', views.list_user, name='list'),
    path('create-user', views.create_user, name='create'),
    path('send', views.send_activation, name='send'),
    path('activate', views.activate, name='activate'),
    path('send-recover', views.send_recover, name='send-recover'),
    path('recover', views.recover_user, name='recover'),

    # Check validation
    path('email-check', views.email_check, name='email-check'),
    path('mobile-check', views.mobile_check, name='mobile-check'),
    path('username-check', views.username_check, name='username-check'),
]
