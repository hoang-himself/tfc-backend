from django.contrib import admin
from .models import metatable, branch, setting, role, user, course, class_metadata, class_student, class_teacher, session, attendance, log

admin.site.register(metatable)
admin.site.register(branch)
admin.site.register(setting)
admin.site.register(role)
admin.site.register(user)
admin.site.register(course)
admin.site.register(class_metadata)
admin.site.register(class_student)
admin.site.register(class_teacher)
admin.site.register(session)
admin.site.register(attendance)
admin.site.register(log)
