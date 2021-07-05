from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import (
    Metatable, Branch, Calendar, Setting, CustomUser, Course,
    ClassMetadata, ClassStudent, Schedule, Attendance, Log
)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = (
        (None, {
            'fields': ('password',)
        }),
        ('Personal info', {
         'fields': ('first_name', 'mid_name', 'last_name', 'email',)
         }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',),
        }),
        ('Important dates', {
         'fields': ('created_at', 'updated_at', 'last_login',)
         }),
    )
    readonly_fields = ('created_at',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'mid_name', 'last_name', 'email', 'password1', 'password2',),
        }),
    )
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('email', 'first_name', 'mid_name',
                    'last_name', 'is_staff', 'is_active')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.register(Metatable)
admin.site.register(Branch)
admin.site.register(Calendar)
admin.site.register(Setting)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Course)
admin.site.register(ClassMetadata)
admin.site.register(ClassStudent)
admin.site.register(Schedule)
admin.site.register(Attendance)
admin.site.register(Log)
