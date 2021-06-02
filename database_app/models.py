from django.db import models

"""
Why use TextField() over CharField() for PostgreSQL
    https://www.postgresql.org/docs/9.0/datatype-character.html
    CharField() costs more storage and CPU
"""


class metatable(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()


class branch(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()


class setting(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    value = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()


class role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(unique=True)
    dashboard = models.BooleanField()
    kanban = models.BooleanField()
    setting = models.BooleanField()
    created_at = models.FloatField()
    updated_at = models.FloatField()


class person(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.TextField(unique=True)
    uid = models.TextField(unique=True)
    first_name = models.TextField()
    last_name = models.TextField()
    birth_date = models.BigIntegerField()
    email = models.TextField(unique=True)
    mobile = models.TextField(unique=True)
    gender = models.BooleanField(null=True)
    password = models.TextField()
    address = models.TextField()
    role_id = models.ForeignKey(role, default='', on_delete=models.CASCADE)
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['first_name', ]),
            models.Index(fields=['last_name', ]),
            models.Index(fields=['birth_date', ]),
            models.Index(fields=['gender', ]),
            models.Index(fields=['role_id', ]),
        ]


class course(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField(unique=True)
    desc = models.TextField()
    short_desc = models.TextField()
    type = models.TextField()
    duration = models.SmallIntegerField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['type', ]),
            models.Index(fields=['duration', ])
        ]


class class_metadata(models.Model):
    id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey(course, default='', on_delete=models.CASCADE)
    name = models.TextField(unique=True)
    status = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['status', ])
        ]


class class_student(models.Model):
    id = models.AutoField(primary_key=True)
    classroom_id = models.ForeignKey(
        class_metadata,
        default='',
        on_delete=models.CASCADE
    )
    student_id = models.ForeignKey(
        person,
        default='',
        on_delete=models.CASCADE)
    created_at = models.FloatField()
    updated_at = models.FloatField()


class class_teacher(models.Model):
    id = models.AutoField(primary_key=True)
    classroom_id = models.ForeignKey(
        class_metadata,
        default='',
        on_delete=models.CASCADE
    )
    teacher_id = models.ForeignKey(
        person,
        default='',
        on_delete=models.CASCADE)
    created_at = models.FloatField()
    updated_at = models.FloatField()


class session(models.Model):
    id = models.AutoField(primary_key=True)
    classroom_id = models.ForeignKey(
        class_metadata,
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


class attendance(models.Model):
    id = models.AutoField(primary_key=True)
    session_id = models.ForeignKey(
        session,
        default='',
        on_delete=models.CASCADE
    )
    student_id = models.ForeignKey(
        person,
        default='',
        on_delete=models.CASCADE
    )
    status = models.BooleanField(null=True)
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
                name='unique_attendance')
        ]


class log(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(
        person,
        default='',
        on_delete=models.DO_NOTHING
    )
    table_id = models.ForeignKey(
        metatable,
        default='',
        on_delete=models.DO_NOTHING
    )
    desc = models.TextField()
    short_desc = models.TextField()
    created_at = models.FloatField()
    updated_at = models.FloatField()
