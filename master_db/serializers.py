from rest_framework import serializers
from master_db.models import (
    Metatable, Branch, Calendar, MyUser, Setting, MyGroup, Course,
    ClassMetadata, ClassStudent, Schedule, Attendance, Log
)

from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField


class MetatableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metatable
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = '__all__'


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = '__all__'


class MyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyGroup
        fields = '__all__'


class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Course
        fields = '__all__'


class UserRelatedField(serializers.RelatedField):
    def to_representation(self, obj):
        return {
            'name': obj.first_name + (' ' if obj.mid_name is None else ' ' + obj.mid_name + ' ') + obj.last_name,
            'mobile': obj.mobile,
            'email': obj.email,
            'uuid': obj.uuid,
        }

class ClassMetadataSerializer(serializers.ModelSerializer):
    students = UserRelatedField(many=True, read_only=True)
    teacher = UserRelatedField(read_only=True)
    
    class Meta:
        model = ClassMetadata
        exclude = ('id', )


class ClassStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassStudent
        fields = '__all__'


class ClassRelatedField(serializers.RelatedField):
    def to_representation(self, obj):
        return {
            'name': obj.name,
            'course': obj.course.name
        }
class ScheduleSerializer(serializers.ModelSerializer):
    classroom = ClassRelatedField(read_only=True)

    class Meta:
        model = Schedule
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'
