from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import (
    MyUserChangeForm, MyUserCreationForm
)
from .models import (
    Metatable, Branch, Setting, Role, MyUser, Course,
    ClassMetadata, ClassStudent, ClassTeacher, Session, Attendance, Log
)


class MyUserAdmin(UserAdmin):
    model = MyUser
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = [
        'email', 'username', 'last_name', 'first_name'
    ]
    fieldsets = UserAdmin.fieldsets + (
        ('Personal', {
            'fields': ('male', 'birth_date', 'mobile', 'address')
        }),
        (None, {
            'fields': ('avatar',)
        }),
    )  # Allows changing these fields in admin module
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name', 'last_name', 'email',
                'birth_date', 'mobile', 'male', 'address',
                'avatar', 'updated_at',
            )
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(Metatable)
admin.site.register(Branch)
admin.site.register(Setting)
admin.site.register(Role)
admin.site.register(MyUser, MyUserAdmin)
admin.site.register(Course)
admin.site.register(ClassMetadata)
admin.site.register(ClassStudent)
admin.site.register(ClassTeacher)
admin.site.register(Session)
admin.site.register(Attendance)
admin.site.register(Log)
