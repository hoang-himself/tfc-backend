from django.contrib import admin

from .models import (
    Metatable, Branch, Setting, Role, MyUser, Course,
    ClassMetadata, ClassStudent, ClassTeacher, Session, Attendance, Log
)


admin.site.register(Metatable)
admin.site.register(Branch)
admin.site.register(Setting)
admin.site.register(Role)
admin.site.register(MyUser)
admin.site.register(Course)
admin.site.register(ClassMetadata)
admin.site.register(ClassStudent)
admin.site.register(ClassTeacher)
admin.site.register(Session)
admin.site.register(Attendance)
admin.site.register(Log)
