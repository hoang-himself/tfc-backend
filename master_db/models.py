from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, Group

import uuid


class Metatable(models.Model):
    name = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    def __str__(self):
        return self.name


class Branch(models.Model):
    addr = models.TextField()
    short_adr = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    def __str__(self):
        return self.short_adr


class Setting(models.Model):
    name = models.TextField()
    value = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.TextField(unique=True)
    student = models.BooleanField(default=False)
    teacher = models.BooleanField(default=False)
    dashboard = models.BooleanField(default=False)
    kanban = models.BooleanField(default=False)
    setting = models.BooleanField(default=False)
    created_at = models.FloatField(default=False)
    updated_at = models.FloatField(default=False)

    def __str__(self):
        return self.name


class MyUser(AbstractUser):
    # id
    # password
    # last_login
    # is_superuser
    # username
    # first_name
    # last_name
    # email
    # is_staff
    # is_active
    # date_joined
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    birth_date = models.FloatField()
    mobile = models.TextField(unique=True)
    male = models.BooleanField(null=True, blank=True)
    address = models.TextField()
    avatar = models.TextField(null=True, blank=True)
    updated_at = models.FloatField()
    # role = models.ForeignKey(Role, default='', on_delete=models.CASCADE, null=True)

    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        'email',
        'birth_date',
        'mobile',
        'male',
        'address',
        'avatar',
        'updated_at',
        # 'role',
    ]

    class Meta:
        indexes = [
            models.Index(fields=['first_name', ]),
            models.Index(fields=['last_name', ]),
            models.Index(fields=['birth_date', ]),
            models.Index(fields=['male', ]),
            # models.Index(fields=['role', ]),
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Course(models.Model):
    name = models.TextField(unique=True)
    desc = models.TextField()
    short_desc = models.TextField()
    cert = models.TextField()
    duration = models.SmallIntegerField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['cert', ]),
            models.Index(fields=['duration', ])
        ]

    def __str__(self):
        return f'{self.cert} {self.name}'


class ClassMetadata(models.Model):
    course = models.ForeignKey(Course, default='', on_delete=models.CASCADE)
    name = models.TextField(unique=True)
    status = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['status', ])
        ]

    def __str__(self):
        return f'{self.status} {self.course} {self.name}'


class ClassStudent(models.Model):
    classroom = models.ForeignKey(
        ClassMetadata,
        default='',
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        get_user_model(),
        default='',
        on_delete=models.CASCADE)
    created_at = models.FloatField()
    updated_at = models.FloatField()

    def __str__(self):
        return f'{self.classrom} {self.student}'


class ClassTeacher(models.Model):
    classroom = models.ForeignKey(
        ClassMetadata,
        default='',
        on_delete=models.CASCADE
    )
    teacher = models.ForeignKey(
        get_user_model(),
        default='',
        on_delete=models.CASCADE)
    created_at = models.FloatField()
    updated_at = models.FloatField()

    def __str__(self):
        return f'{self.classroom} {self.teacher}'


class Session(models.Model):
    classroom = models.ForeignKey(
        ClassMetadata,
        default='',
        on_delete=models.CASCADE
    )
    time_start = models.FloatField()
    time_end = models.FloatField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['time_start', 'time_end'])
        ]

    def __str__(self):
        return f'{self.classroom} {self.time_start} {self.time_end}'


class Attendance(models.Model):
    session = models.ForeignKey(
        Session,
        default='',
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        get_user_model(),
        default='',
        on_delete=models.CASCADE
    )
    status = models.BooleanField(null=True, blank=True)
    date = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['status', ])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'date'],
                name='unique_attendance'
            )
        ]

    def __str__(self):
        return f'{self.session} {self.status} {self.student}'


class Log(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        default='',
        on_delete=models.DO_NOTHING
    )
    table = models.ForeignKey(
        Metatable,
        default='',
        on_delete=models.DO_NOTHING
    )
    desc = models.TextField()
    short_desc = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    def __str__(self):
        return self.short_desc
