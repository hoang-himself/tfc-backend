from django.contrib.auth.models import AbstractUser
from django.db import models


class role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=255)
    role_dashboard = models.BooleanField()
    role_kanban = models.BooleanField()
    role_setting = models.BooleanField()
    role_created_at = models.FloatField()
    role_updated_at = models.FloatField()


class user(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_fname = models.CharField(max_length=255)
    user_lname = models.CharField(max_length=255)
    user_dob = models.BigIntegerField()
    user_email = models.CharField(max_length=255, unique=True)
    user_mobile = models.CharField(max_length=12, unique=True)
    user_uid = models.CharField(max_length=255, unique=True)
    user_gender = models.BooleanField(null=True)
    user_password = models.CharField(max_length=255)
    user_addr = models.CharField(max_length=255)
    user_role = models.ForeignKey(role, default='', on_delete=models.CASCADE)
    user_created_at = models.FloatField()
    user_updated_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['user_fname', ]),
            models.Index(fields=['user_lname', ]),
            models.Index(fields=['user_dob', ]),
            models.Index(fields=['user_gender', ]),
            models.Index(fields=['user_role', ]),
        ]


class setting(models.Model):
    setting_id = models.AutoField(primary_key=True)
    setting_label = models.CharField(max_length=255)
    setting_value = models.TextField()
    setting_created_at = models.FloatField()
    setting_updated_at = models.FloatField()


class course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=255, unique=True)
    course_des = models.TextField()
    course_short_des = models.CharField(max_length=255)
    course_type = models.CharField(max_length=255)
    course_duration = models.SmallIntegerField()
    setting_created_at = models.FloatField()
    setting_updated_at = models.FloatField()

    indexes = [
        models.Index(fields=['course_type', ]),
        models.Index(fields=['course_duration', ])
    ]


class classes(models.Model):
    classes_id = models.AutoField(primary_key=True)
    classes_course = models.ForeignKey(
        course, default='', on_delete=models.CASCADE)
    classes_name = models.CharField(max_length=255, unique=True)
    classes_status = models.CharField(max_length=255)
    classes_created_at = models.FloatField()
    classes_updated_at = models.FloatField()

    indexes = [
        models.Index(fields=['classes_status', ])
    ]


class student_classes(models.Model):
    student = models.ForeignKey(user, default='', on_delete=models.CASCADE)
    classes = models.ForeignKey(classes, default='', on_delete=models.CASCADE)
    student_classes_created_at = models.FloatField()
    student_classes_updated_at = models.FloatField()


class schedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    schedule_classes = models.ForeignKey(
        classes, default='', on_delete=models.CASCADE)
    schedule_start = models.FloatField()
    schedule_end = models.FloatField()
    schedule_created_at = models.FloatField()
    schedule_updated_at = models.FloatField()


class attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    attendance_student = models.ForeignKey(
        user, default='', on_delete=models.CASCADE)
    attendance_schedule = models.ForeignKey(
        schedule, default='', on_delete=models.CASCADE)
    attendance_status = models.BooleanField(null=True)
    attendance_date = models.CharField(max_length=255)
    attendance_created_at = models.FloatField()
    attendance_updated_at = models.FloatField()

    indexes = [
        models.Index(fields=['attendance_status', ])
    ]

    unique_together = (('attendance_student', 'attendance_date'))
