from rest_framework import serializers
from rest_framework.utils import representation
from master_db.models import (
    Metatable, Branch, Calendar, MyUser, Setting, MyGroup, Course,
    ClassMetadata, ClassStudent, Schedule, Attendance, Log
)
from django.db import models

from collections import OrderedDict
from rest_framework.fields import SkipField

from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.relations import PKOnlyObject


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

# Enhanced models: Add ignoring fields feauture when call data property


class EnhancedListSerializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(self.child, EnhancedModelSerializer):
            raise TypeError(
                "To use EnhancedListSerializer the origin serializer must be EnhancedModelSerializer")

    def add_ignore_field(self, field):
        if getattr(self.child, 'ignore', None) is None:
            self.child.ignore = [field]
        else:
            self.child.ignore.append(field)

    def clear_ignore(self):
        if getattr(self.child, 'ignore', None) is not None:
            del self.child.ignore


class EnhancedModelSerializer(serializers.ModelSerializer):
    def add_ignore_field(self, field):
        if getattr(self, 'ignore', None) is None:
            self.ignore = [field]
        else:
            self.ignore.append(field)

    def clear_ignore(self):
        if getattr(self, 'ignore', None) is not None:
            del self.ignore

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """

        ret = OrderedDict()

        fields = []
        ignore = getattr(self, 'ignore', [])

        # This is the key to override this class's parent method
        for key, field in self.fields.items():
            if not field.read_only and not key in ignore:
                fields.append(field)

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            check_for_none = attribute.pk if isinstance(
                attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


class UserRelatedField(serializers.RelatedField):
    def to_representation(self, obj):
        return {
            'name': obj.first_name + (' ' if obj.mid_name is None else ' ' + obj.mid_name + ' ') + obj.last_name,
            'mobile': obj.mobile,
            'email': obj.email,
            'uuid': obj.uuid,
        }


class ClassMetadataSerializer(EnhancedModelSerializer):
    students = UserRelatedField(many=True, read_only=True)
    teacher = UserRelatedField(read_only=True)

    class Meta:
        model = ClassMetadata
        exclude = ('id', )
        list_serializer_class = EnhancedListSerializer


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
