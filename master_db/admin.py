from django.contrib import admin

from .models import (
    Metatable, Branch, Calendar, Setting, Role, MyUser, Course,
    ClassMetadata, ClassStudent, ClassTeacher, Schedule, Attendance, Log
)


admin.site.register(Metatable)
admin.site.register(Branch)
admin.site.register(Calendar)
admin.site.register(Setting)
admin.site.register(Role)
admin.site.register(MyUser)
admin.site.register(Course)
admin.site.register(ClassMetadata)
admin.site.register(ClassStudent)
admin.site.register(ClassTeacher)
admin.site.register(Schedule)
admin.site.register(Attendance)
admin.site.register(Log)
