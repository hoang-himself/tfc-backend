from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager

from .managers import CustomUserManager

import uuid
import datetime
import os


PHONE_REGEX = r'^(0)(3[2-9]|5[689]|7[06-9]|8[0-689]|9[0-46-9])[0-9]{7}$'
USER_IMAGE_PATH = 'images/users/'


class TemplateBase(models.base.ModelBase):
    """
        Metaclass for saving editable of every field
    """
    def __new__(cls, name, bases, attrs, **kwargs):
        editableDict = {}
        for field_name, field in attrs.items():
            if isinstance(field, models.Field):
                editableDict[field_name] = field.editable
        ret = super().__new__(cls, name, bases, attrs, **kwargs)
        ret.editable_fields = editableDict
        return ret


class TemplateModel(TimeStampedModel, metaclass=TemplateBase):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
    desc = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


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


def upload_avatar(instance, filename):
    file_ext = os.path.splitext(filename)[1]
    return '%s/%s/%s' % (USER_IMAGE_PATH, instance.uuid, 'profile' + file_ext)


class CustomUser(AbstractUser, metaclass=TemplateBase):
    username = None
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, blank=True)
    email = models.EmailField(unique=True)

    birth_date = models.DateField(null=True, blank=True)
    mobile = models.CharField(
        validators=[RegexValidator(
            regex=PHONE_REGEX, message="Invalid phone number")],
        max_length=15,
        unique=True
    )
    male = models.BooleanField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    avatar = models.ImageField(
        upload_to=upload_avatar, null=True, blank=True)

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
        return self.first_name + ' ' + self.last_name


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


# TODO
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
            models.Index(fields=['course', ]),
            models.Index(fields=['status', ]),
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
        indexes = [
            models.Index(fields=['time_start', 'time_end'])
        ]

    def __str__(self):
        time_start = datetime.datetime.fromtimestamp(self.time_start)
        time_end = datetime.datetime.fromtimestamp(self.time_end)
        return f'{self.classroom}, {time_start.hour}:{time_start.minute:02d} ~ {time_end.hour}:{time_end.minute:02d}'


#
class Session(TemplateModel):
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        editable=False
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        editable=False
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
        return f'{str(self.student)} in {str(self.schedule)}'


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
        return f'{self.name}'


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
