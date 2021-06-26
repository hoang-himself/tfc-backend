from django.db import models

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
    class_session = models.BooleanField(default=False)
    account_cred = models.BooleanField(default=False)
    kanban = models.BooleanField(default=False)
    setting = models.BooleanField(default=False)
    created_at = models.FloatField(default=False)
    updated_at = models.FloatField(default=False)

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
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True, blank=True)
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['first_name', ]),
            models.Index(fields=['last_name', ]),
            models.Index(fields=['birth_date', ]),
            models.Index(fields=['male', ]),
            models.Index(fields=['role', ]),
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
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
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
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE)
    created_at = models.FloatField()
    updated_at = models.FloatField()

    def __str__(self):
        return f'{self.classrom} {self.student}'


class ClassTeacher(models.Model):
    classroom = models.ForeignKey(
        ClassMetadata,
        on_delete=models.CASCADE
    )
    teacher = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE)
    created_at = models.FloatField()
    updated_at = models.FloatField()

    def __str__(self):
        return f'{self.classroom} {self.teacher}'


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
        indexes = [
            models.Index(fields=['time_start', 'time_end'])
        ]

    def __str__(self):
        return f'{self.classroom} {self.time_start} {self.time_end}'


class Attendance(models.Model):
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        MyUser,
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
        return f'{self.schedule} {self.status} {self.student}'


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
        return f'{self.name}, {self.time_start} ~ {self.time_end}'


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


class BlacklistedToken(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.DO_NOTHING)
    token = models.TextField()
    blacklisted_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['blacklisted_at'])
        ]
