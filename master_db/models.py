from django.contrib.auth.models import AbstractUser
from django.db import models
from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager

from .managers import CustomUserManager

import uuid
import datetime


#
class Metatable(TimeStampedModel):
    name = models.TextField(unique=True)

    class Meta:
        verbose_name = 'table'
        verbose_name_plural = 'tables'

    def __str__(self):
        return self.name


#
class Branch(TimeStampedModel):
    addr = models.TextField()
    short_adr = models.TextField()
    phone = models.TextField()

    class Meta:
        verbose_name = 'branch'
        verbose_name_plural = 'branches'

    def __str__(self):
        return self.short_adr


#
class Setting(TimeStampedModel):
    name = models.TextField()
    value = models.TextField()

    class Meta:
        verbose_name = 'setting'
        verbose_name_plural = 'settings'

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    username = None
    uuid = models.UUIDField(default=uuid.uuid4, blank=True)
    email = models.EmailField(unique=True)

    first_name = models.TextField()
    mid_name = models.TextField(null=True, blank=True)
    last_name = models.TextField()
    birth_date = models.DateField()
    mobile = models.CharField(max_length=12, unique=True)
    male = models.BooleanField(null=True, blank=True)
    address = models.TextField()
    avatar = models.ImageField(
        upload_to='images/profile/%Y/%m/%d/', null=True, blank=True)

    date_joined = models.DateTimeField(
        'date joined', auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(
        'date updated', auto_now=True)  # Auto update for every save()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'first_name',
        'mid_name',
        'last_name',
        'birth_date',
        'mobile',
        'male',
        'address',
    ]
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        indexes = [
            models.Index(fields=['first_name', ]),
            models.Index(fields=['last_name', ]),
            models.Index(fields=['birth_date', ]),
            models.Index(fields=['male', ]),
        ]

    def __str__(self):
        return self.email


#
class Course(TimeStampedModel):
    name = models.TextField(unique=True)
    desc = models.TextField()
    short_desc = models.TextField()
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
class ClassMetadata(TimeStampedModel):
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
class Schedule(TimeStampedModel):
    classroom = models.ForeignKey(
        ClassMetadata,
        on_delete=models.CASCADE,
    )
    time_start = models.IntegerField()
    time_end = models.IntegerField()

    class Meta:
        verbose_name = 'session'
        verbose_name_plural = 'sessions'
        indexes = [
            models.Index(fields=['time_start', 'time_end'])
        ]

    def __str__(self):
        time_start = datetime.datetime.fromtimestamp(self.time_start)
        time_end = datetime.datetime.fromtimestamp(self.time_end)
        return f'{self.classroom}, {time_start.hour}:{time_start.minute:02d} ~ {time_end.hour}:{time_end.minute:02d}'


#
class ClassStudent(TimeStampedModel):
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
class Attendance(TimeStampedModel):
    session = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    status = models.BooleanField(null=True, blank=True)

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
class Calendar(TimeStampedModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE
    )
    name = models.TextField()
    desc = models.TextField(null=True, blank=True)
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
class Log(TimeStampedModel):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.DO_NOTHING
    )
    table = models.ForeignKey(
        Metatable,
        on_delete=models.DO_NOTHING
    )
    desc = models.TextField()
    short_desc = models.TextField()

    def __str__(self):
        return self.short_desc
