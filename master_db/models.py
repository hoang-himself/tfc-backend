from django.contrib.auth.models import AbstractUser
from django.db import models

from model_utils.fields import (AutoCreatedField, AutoLastModifiedField)
from taggit.managers import TaggableManager

from .managers import CustomUserManager

import uuid
import datetime


class TemplateModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
    created_at = AutoCreatedField('created')
    updated_at = AutoLastModifiedField('updated')
    desc = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Overriding the save method in order to make sure that
        modified field is updated even if it is not given as
        a parameter to the update field argument.
        """
        update_fields = kwargs.get('update_fields', None)
        if update_fields:
            kwargs['update_fields'] = set(update_fields).union({'updated_at'})

        super().save(*args, **kwargs)


#
class Metatable(TemplateModel):
    name = models.TextField(unique=True)

    class Meta:
        verbose_name = 'table'
        verbose_name_plural = 'tables'

    def __str__(self):
        return self.name


#
class Branch(TemplateModel):
    addr = models.TextField()
    short_adr = models.TextField()
    phone = models.TextField()

    class Meta:
        verbose_name = 'branch'
        verbose_name_plural = 'branches'

    def __str__(self):
        return self.short_adr


#
class Setting(TemplateModel):
    name = models.TextField()
    value = models.TextField()

    class Meta:
        verbose_name = 'setting'
        verbose_name_plural = 'settings'

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    username = None
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
    email = models.EmailField(unique=True)

    birth_date = models.DateField(null=True, blank=True)
    mobile = models.CharField(max_length=15, unique=True)
    male = models.BooleanField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    avatar = models.ImageField(
        upload_to='images/profile/%Y/%m/%d/', null=True, blank=True)

    date_joined = models.DateTimeField(
        'date joined', auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(
        'date updated', auto_now=True)  # Auto update for every save()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'mobile',
    ]
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        indexes = [
            models.Index(fields=['first_name', ]),
            models.Index(fields=['male', ]),
        ]

    def __str__(self):
        return self.email


#
class Course(TemplateModel):
    name = models.TextField(unique=True)
    tags = TaggableManager()
    duration = models.SmallIntegerField()

    class Meta:
        verbose_name = 'course'
        verbose_name_plural = 'courses'
        indexes = [
            models.Index(fields=['duration', ])
        ]

    def __str__(self):
        return f'{self.name}'


#
class ClassMetadata(TemplateModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.TextField(unique=True)
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.DO_NOTHING,
        related_name='teacher_classes',
        blank=True,
        null=True
    )
    students = models.ManyToManyField(
        CustomUser,
        related_name='student_classes',
        blank=True
    )
    status = models.TextField()

    class Meta:
        verbose_name = 'class'
        verbose_name_plural = 'classes'
        indexes = [
            models.Index(fields=['status', ])
        ]

    def __str__(self):
        return f'{self.name} {self.course} {self.status}'


# Schedule for students
class Schedule(TemplateModel):
    classroom = models.ForeignKey(
        ClassMetadata,
        on_delete=models.CASCADE,
    )
    time_start = models.IntegerField()
    time_end = models.IntegerField()

    class Meta:
        verbose_name = 'schedule'
        verbose_name_plural = 'schedules'
        indexes = [
            models.Index(fields=['time_start', 'time_end'])
        ]

    def __str__(self):
        time_start = datetime.datetime.fromtimestamp(self.time_start)
        time_end = datetime.datetime.fromtimestamp(self.time_end)
        return f'{self.classroom}, {time_start.hour}:{time_start.minute:02d} ~ {time_end.hour}:{time_end.minute:02d}'


#
class ClassStudent(TemplateModel):
    classroom = models.ForeignKey(
        ClassMetadata,
        on_delete=models.CASCADE,
        null=True
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'class student'
        verbose_name_plural = 'class students'

    def __str__(self):
        return f'{self.classroom} {self.student}'


#
class Session(TemplateModel):
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    homework = models.SmallIntegerField(null=True, blank=True)
    status = models.BooleanField(null=True, blank=True)

    class Meta:
        verbose_name = 'session'
        verbose_name_plural = 'sessions'
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['schedule', ])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'schedule'],
                name='unique_session'
            )
        ]

    def __str__(self):
        return f'{self.schedule} {self.status} {self.student}'


# Calendar for staff only
class Calendar(TemplateModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    name = models.TextField()
    time_start = models.FloatField()
    time_end = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['time_start', 'time_end'])
        ]

    def __str__(self):
        time_start = datetime.datetime.fromtimestamp(self.time_start)
        time_end = datetime.datetime.fromtimestamp(self.time_end)
        return f'{self.name}, {time_start.hour + time_start.minute / 60} ~ {time_end.hour + time_end.minute / 60}'


#
class Log(TemplateModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.DO_NOTHING
    )
    table = models.ForeignKey(
        Metatable,
        on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return self.short_desc
