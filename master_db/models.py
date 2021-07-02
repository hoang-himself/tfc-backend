from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import Group, AbstractUser
from django.utils.translation import gettext_lazy as _

from taggit.managers import TaggableManager

import uuid
import datetime


class LowerTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        super(LowerTextField, self).__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return str(value).lower()


#
class Metatable(models.Model):
    name = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        verbose_name = 'table'
        verbose_name_plural = 'tables'

    def __str__(self):
        return self.name


#
class Branch(models.Model):
    addr = models.TextField()
    short_adr = models.TextField()
    phone = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        verbose_name = 'branch'
        verbose_name_plural = 'branches'

    def __str__(self):
        return self.short_adr


#
class Setting(models.Model):
    name = models.TextField()
    value = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        verbose_name = 'setting'
        verbose_name_plural = 'settings'

    def __str__(self):
        return self.name


#
class MyGroup(Group):
    created_at = models.FloatField(default=False)
    updated_at = models.FloatField(default=False)

    class Meta:
        verbose_name = 'group'
        verbose_name_plural = 'groups'

    def __unicode__(self):
        return self.__str__

    def __str__(self):
        return self.name


class MyUser(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    username = models.TextField(unique=True)
    first_name = models.TextField()
    mid_name = models.TextField(null=True, blank=True)
    last_name = models.TextField()
    email = models.EmailField(unique=True)
    password = models.TextField()
    birth_date = models.FloatField()
    mobile = models.TextField(unique=True)
    male = models.BooleanField(null=True, blank=True)
    address = models.TextField()
    avatar = models.ImageField(
        upload_to='images/profile/%Y/%m/%d/', null=True, blank=True)
    # group = models.ForeignKey(MyGroup, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, blank=True)
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['first_name', ]),
            models.Index(fields=['last_name', ]),
            models.Index(fields=['birth_date', ]),
            models.Index(fields=['male', ]),
            # models.Index(fields=['group', ]),
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


#
class Course(models.Model):
    name = models.TextField(unique=True)
    desc = models.TextField()
    short_desc = models.TextField()
    tags = TaggableManager()
    duration = models.SmallIntegerField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        verbose_name = 'course'
        verbose_name_plural = 'courses'
        indexes = [
            models.Index(fields=['duration', ])
        ]

    def __str__(self):
        return f'{self.name}'


#
class ClassMetadata(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.TextField(unique=True)
    teacher = models.ForeignKey(
        MyUser,
        on_delete=models.DO_NOTHING,
        related_name='teacher_classes',
        blank=True
    )
    students = models.ManyToManyField(
        MyUser,
        related_name='students_classes',
        blank=True
    )
    status = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        verbose_name = 'class'
        verbose_name_plural = 'classes'
        indexes = [
            models.Index(fields=['status', ])
        ]

    def __str__(self):
        return f'{self.status} {self.course} {self.name}'


# Schedule for students
class Schedule(models.Model):
    classroom = models.ForeignKey(
        ClassMetadata,
        on_delete=models.CASCADE
    )
    time_start = models.FloatField()
    time_end = models.FloatField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        verbose_name = 'session'
        verbose_name_plural = 'sessions'
        indexes = [
            models.Index(fields=['time_start', 'time_end'])
        ]

    def __str__(self):
        time_start = datetime.datetime.fromtimestamp(self.time_start)
        time_end = datetime.datetime.fromtimestamp(self.time_end)
        return f'{self.classroom}, {time_start.hour + time_start.minute / 60} ~ {time_end.hour + time_end.minute / 60}'


#
class ClassStudent(models.Model):
    classroom = models.ForeignKey(
        ClassMetadata,
        on_delete=models.CASCADE,
        null=True
    )
    student = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE)
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        verbose_name = 'class student'
        verbose_name_plural = 'class students'

    def __str__(self):
        return f'{self.classrom} {self.student}'


#
class Attendance(models.Model):
    session = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE
    )
    status = models.BooleanField(null=True, blank=True)
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        verbose_name = 'attendance'
        verbose_name_plural = 'attendances'
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['session', ])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'session'],
                name='unique_attendance'
            )
        ]

    def __str__(self):
        return f'{self.schedule} {self.status} {self.student}'


# Calendar for staff only
class Calendar(models.Model):
    user = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE
    )
    name = models.TextField()
    desc = models.TextField(null=True, blank=True)
    time_start = models.FloatField()
    time_end = models.FloatField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['time_start', 'time_end'])
        ]

    def __str__(self):
        time_start = datetime.datetime.fromtimestamp(self.time_start)
        time_end = datetime.datetime.fromtimestamp(self.time_end)
        return f'{self.name}, {time_start.hour + time_start.minute / 60} ~ {time_end.hour + time_end.minute / 60}'


#
class Log(models.Model):
    user = models.ForeignKey(
        MyUser,
        on_delete=models.DO_NOTHING
    )
    table = models.ForeignKey(
        Metatable,
        on_delete=models.DO_NOTHING
    )
    desc = models.TextField()
    short_desc = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    def __str__(self):
        return self.short_desc


#
class BlacklistedToken(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.DO_NOTHING)
    token = models.TextField()
    blacklisted_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['blacklisted_at'])
        ]
