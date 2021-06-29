from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin

from .models import (
    Metatable, Branch, Calendar, Setting, MyGroup, MyUser, Course,
    ClassMetadata, ClassStudent, ClassTeacher, Schedule, Attendance, Log
)


class MyUserAdmin(admin.ModelAdmin):
    search_fields = ['username', 'first_name', 'last_name', 'email', 'mobile']


admin.site.unregister(Group)
admin.site.register(Metatable)
admin.site.register(Branch)
admin.site.register(Calendar)
admin.site.register(Setting)
admin.site.register(MyGroup, GroupAdmin)
admin.site.register(MyUser)
admin.site.register(Course)
admin.site.register(ClassMetadata)
admin.site.register(ClassStudent)
admin.site.register(ClassTeacher)
admin.site.register(Schedule)
admin.site.register(Attendance)
admin.site.register(Log)
