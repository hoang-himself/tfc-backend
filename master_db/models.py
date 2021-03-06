from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager

from .managers import CustomUserManager

import uuid
import os

PHONE_REGEX = r'^(0)(3[2-9]|5[689]|7[06-9]|8[0-689]|9[0-46-9])[0-9]{7}$'
USER_IMAGE_PATH = 'users/'


class TemplateModel(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
    desc = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


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


def upload_avatar(instance, filename):
    file_ext = os.path.splitext(filename)[1]
    return '%s/%s/%s' % (USER_IMAGE_PATH, instance.uuid, 'profile' + file_ext)


class CustomUser(AbstractUser):
    username = None
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
    email = models.EmailField(unique=True)

    birth_date = models.DateField(null=True, blank=True)
    mobile = models.CharField(
        validators=[
            RegexValidator(regex=PHONE_REGEX, message="Invalid phone number")
        ],
        max_length=15,
        unique=True
    )
    male = models.BooleanField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to=upload_avatar, null=True, blank=True)

    date_joined = models.DateTimeField(
        'date joined', auto_now_add=True, editable=False
    )
    date_updated = models.DateTimeField(
        'date updated', auto_now=True
    )  # Auto update for every save()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'mobile',
    ]
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        indexes = [
            models.Index(fields=[
                'first_name',
            ]),
            models.Index(fields=[
                'male',
            ]),
        ]

    def __str__(self):
        return self.first_name + ' ' + self.last_name


#
class Course(TemplateModel):
    name = models.TextField(unique=True)
    tags = TaggableManager()
    duration = models.SmallIntegerField()

    class Meta:
        verbose_name = 'course'
        verbose_name_plural = 'courses'
        indexes = [models.Index(fields=[
            'duration',
        ])]

    def __str__(self):
        return f'{self.name}'


class ClassMetadata(TemplateModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.TextField(unique=True)
    teacher = models.ForeignKey(
        CustomUser,
        related_name='teacher_classes',
        on_delete=models.DO_NOTHING,
        null=True,
    )
    students = models.ManyToManyField(
        CustomUser,
        related_name='student_classes',
        blank=True,
    )
    status = models.TextField()

    class Meta:
        verbose_name = 'class'
        verbose_name_plural = 'classes'
        indexes = [
            models.Index(fields=[
                'course',
            ]),
            models.Index(fields=[
                'status',
            ]),
        ]

    def __str__(self):
        return f'{self.name}'


# Schedule for students
class Schedule(TemplateModel):
    classroom = models.ForeignKey(
        ClassMetadata,
        on_delete=models.CASCADE,
    )
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()

    class Meta:
        verbose_name = 'schedule'
        verbose_name_plural = 'schedules'
        indexes = [models.Index(fields=['time_start', 'time_end'])]

    def __str__(self):
        return (
            f'{self.classroom}, '
            f'{self.time_start.hour}:{self.time_start.minute:02d}'
            f' ~ {self.time_end.hour}:{self.time_end.minute:02d}'
        )


#
class Session(TemplateModel):
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
    )
    homework = models.SmallIntegerField(null=True, blank=True)
    status = models.BooleanField(null=True, blank=True)

    class Meta:
        verbose_name = 'session'
        verbose_name_plural = 'sessions'
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=[
                'schedule',
            ])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'schedule'], name='unique_session'
            )
        ]

    def __str__(self):
        return f'{str(self.student)} in {str(self.schedule)}'


# Calendar for staff only
class Calendar(TemplateModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.TextField()
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()

    class Meta:
        indexes = [models.Index(fields=['time_start', 'time_end'])]

    def __str__(self):
        return f'{self.name}'


#
class Log(TemplateModel):
    """
    #TODO
    user = models.TextField()
    action = models.TextField()
    entity = models.TextField()
    table = models.TextField()

    # desc = f'User {self.user} {self.action} {self.entity} in table {self.table}
    Eg: User ffffff-ffff-ffff-ffffff created aaaaaa-aaaa-aaaa-aaaaaa in table Class

    Either use custom function or manager
    """

    def __str__(self):
        return self.desc
