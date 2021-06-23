from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import MyUser


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm):
        model = MyUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'is_active',
            'birth_date', 'mobile', 'male', 'address', 'avatar',
        )


class MyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = MyUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'is_active',
            'birth_date', 'mobile', 'male', 'address', 'avatar',
        )
