from rest_framework import serializers
from master_db.models import metatable, branch, setting, role, user, course, class_metadata, class_student, class_teacher, session, attendance, log


class MetatableSerializer(serializers.ModelSerializer):
    class Meta:
        model = metatable
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = branch
        fields = '__all__'


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = setting
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = course
        fields = '__all__'


class ClassMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = class_metadata
        fields = '__all__'


class ClassStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = class_student
        fields = '__all__'


class ClassTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = class_teacher
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = session
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = attendance
        fields = '__all__'


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = log
        fields = '__all__'
