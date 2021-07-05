from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import (
    Metatable, Branch, Calendar, Setting, CustomUser, Course,
    ClassMetadata, ClassStudent, Schedule, Attendance, Log
)


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active',)
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)


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
