from rest_framework import serializers
from master_db.models import (
    Metatable, Branch, Setting, Role, MyUser, Course,
    ClassMetadata, ClassStudent, ClassTeacher, Session, Attendance, Log
)


class MetatableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metatable
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class ClassMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassMetadata
        fields = '__all__'


class ClassStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassStudent
        fields = '__all__'


class ClassTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTeacher
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'
