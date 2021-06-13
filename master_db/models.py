from django.db import models
from django.contrib.auth.models import AbstractUser

"""
Why use TextField() over CharField() for PostgreSQL
    https://www.postgresql.org/docs/9.0/datatype-character.html
    CharField() costs more storage and CPU
"""


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
    student = models.BooleanField()
    teacher = models.BooleanField()
    dashboard = models.BooleanField()
    kanban = models.BooleanField()
    setting = models.BooleanField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    def __str__(self):
        return self.name


class User(models.Model):
    uuid = models.TextField(unique=True)
    uid = models.TextField(unique=True)
    first_name = models.TextField()
    last_name = models.TextField()
    birth_date = models.BigIntegerField()
    email = models.TextField(unique=True)
    mobile = models.TextField(unique=True)
    male = models.BooleanField(null=True, blank=True)
    password = models.TextField()
    address = models.TextField()
    role_id = models.ForeignKey(Role, default='', on_delete=models.CASCADE)
    avatar = models.TextField(null=True, blank=True)
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['first_name', ]),
            models.Index(fields=['last_name', ]),
            models.Index(fields=['birth_date', ]),
            models.Index(fields=['male', ]),
            models.Index(fields=['role_id', ]),
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Course(models.Model):
    id = models.AutoField(primary_key=True)
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
    id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(Course, default='', on_delete=models.CASCADE)
    name = models.TextField(unique=True)
    status = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['status', ])
        ]

    def __str__(self):
        return f'{self.status} {self.course_id} {self.name}'


class ClassStudent(models.Model):
    id = models.AutoField(primary_key=True)
    classroom_id = models.ForeignKey(
        ClassMetadata,
        default='',
        on_delete=models.CASCADE
    )
    student_id = models.ForeignKey(
        User,
        default='',
        on_delete=models.CASCADE)
    created_at = models.FloatField()
    updated_at = models.FloatField()

    def __str__(self):
        return f'{self.classrom_id} {self.student_id}'


class ClassTeacher(models.Model):
    id = models.AutoField(primary_key=True)
    classroom_id = models.ForeignKey(
        ClassMetadata,
        default='',
        on_delete=models.CASCADE
    )
    teacher_id = models.ForeignKey(
        User,
        default='',
        on_delete=models.CASCADE)
    created_at = models.FloatField()
    updated_at = models.FloatField()

    def __str__(self):
        return f'{self.classroom_id} {self.teacher_id}'


class Session(models.Model):
    id = models.AutoField(primary_key=True)
    classroom_id = models.ForeignKey(
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
        return f'{self.classroom_id} {self.time_start} {self.time_end}'


class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    session_id = models.ForeignKey(
        Session,
        default='',
        on_delete=models.CASCADE
    )
    student_id = models.ForeignKey(
        User,
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
                fields=['student_id', 'date'],
                name='unique_attendance'
            )
        ]

    def __str__(self):
        return f'{self.session_id} {self.status} {self.student_id}'


class Log(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(
        User,
        default='',
        on_delete=models.DO_NOTHING
    )
    table_id = models.ForeignKey(
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
