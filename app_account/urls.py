from django.urls import path
from . import views

urlpatterns = [
    path('create', views.create_user, name='create'),
    path('list', views.listUser, name='list'),
    path('create-user', views.create_user, name='create'),
    path('send', views.sendActivation, name='send'),
    path('activate', views.activate, name='activate'),
    path('send-recover', views.sendRecover, name='send-recover'),
    path('recover', views.recoverUser, name='recover'),
    
    # Check validation
    path('email-check', views.emailCheck, name='email-check'),
    path('mobile-check', views.mobileCheck, name='mobile-check'),
    path('username-check', views.usernameCheck, name='username-check'),
]
