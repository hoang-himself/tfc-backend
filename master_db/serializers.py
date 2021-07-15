from django.contrib.auth.models import Group
from rest_framework import serializers
from master_db.models import (
    Metatable, Branch, Calendar, CustomUser, Setting, Course,
    ClassMetadata, ClassStudent, Schedule, Session, Log
)
from taggit_serializer.serializers import (
    TaggitSerializer, TagListSerializerField
)

# For enhanced models


# Enhanced models: Add excluding fields feature
class EnhancedListSerializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(self.child, EnhancedModelSerializer):
            raise TypeError(
                f"To use EnhancedListSerializer, {self.child.__class__.__name__} must inherit from EnhancedModelSerializer")

    def exclude_field(self, field):
        self.child.exclude_field(field)
        return self


class EnhancedModelSerializer(serializers.ModelSerializer):
    def __new__(cls, *args, **kwargs):
        meta = getattr(cls, 'Meta', None)
        if not hasattr(meta, 'list_serializer_class'):
            setattr(meta, 'list_serializer_class', EnhancedListSerializer)
        elif not issubclass(meta.list_serializer_class, EnhancedListSerializer):
            raise TypeError(
                f"In {cls.__name__}, list_serializer_class must be a class inherit from EnhancedListSerializer")

        return super().__new__(cls, *args, **kwargs)

    def exclude_field(self, field):
        try:
            self.fields.pop(field)
        except:
            raise KeyError(
                f"There is no `{field}` field in {self.__class__.__name__} to call exclude_field()")

        return self

    def exclude_created_updated(self):
        return self.exclude_field('created_at').exclude_field('updated_at')


class MetatableSerializer(EnhancedModelSerializer):
    class Meta:
        model = Metatable
        fields = '__all__'


class BranchSerializer(EnhancedModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class CalendarSerializer(EnhancedModelSerializer):
    class Meta:
        model = Calendar
        fields = '__all__'


class SettingSerializer(EnhancedModelSerializer):
    class Meta:
        model = Setting
        fields = '__all__'


class GroupSerializer(EnhancedModelSerializer):
    class Meta:
        model = Group
        fields = ['name', ]


class CustomUserSerializer(EnhancedModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        exclude = ('id', 'password', 'avatar',)


class InternalCustomUserSerializer(EnhancedModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class CourseSerializer(EnhancedModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Course
        fields = '__all__'


class UserRelatedField(serializers.RelatedField):
    def to_representation(self, obj):
        return {
            'name': obj.first_name + obj.last_name,
            'mobile': obj.mobile,
            'email': obj.email,
            'uuid': obj.uuid,
        }


class CourseRelatedField(serializers.RelatedField):
    def to_representation(self, obj):
        return {
            'name': obj.name,
        }


class ClassMetadataSerializer(EnhancedModelSerializer):
    course = CourseRelatedField(read_only=True)
    teacher = UserRelatedField(read_only=True)

    class Meta:
        model = ClassMetadata
        exclude = ('id', )


class ClassStudentSerializer(EnhancedModelSerializer):
    student = UserRelatedField(read_only=True)

    class Meta:
        model = ClassStudent
        fields = '__all__'


class ClassRelatedField(serializers.RelatedField):
    def to_representation(self, obj):
        return {
            'name': obj.name,
            'course': obj.course.name
        }


class ScheduleSerializer(EnhancedModelSerializer):
    classroom = ClassRelatedField(read_only=True)

    class Meta:
        model = Schedule
        fields = '__all__'


class ScheduleRelatedField(serializers.RelatedField):
    def to_representation(self, obj):
        return ScheduleSerializer(obj).exclude_created_updated().data


class SessionSerializer(EnhancedModelSerializer):
    student = UserRelatedField(read_only=True)
    session = ScheduleRelatedField(read_only=True)

    class Meta:
        model = Session
        exclude = ('id', )


class LogSerializer(EnhancedModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'
