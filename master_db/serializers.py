from rest_framework import serializers
from master_db.models import (
    Metatable, Branch, Calendar, MyUser, Setting, MyGroup, Course,
    ClassMetadata, ClassStudent, Schedule, Attendance, Log
)
from taggit_serializer.serializers import TaggitSerializer, TagListSerializerField

# For enhanced models
from collections import OrderedDict
from rest_framework.fields import SkipField, empty
from rest_framework.relations import PKOnlyObject


# Enhanced models: Add ignoring fields feauture when call data property
class EnhancedListSerializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(self.child, EnhancedModelSerializer):
            raise TypeError(
                "To use EnhancedListSerializer the origin serializer must be EnhancedModelSerializer")

    def add_ignore_field(self, field):
        self.child.add_ignore_field(field)

    def clear_ignore(self):
        self.child.clear_ignore()


class EnhancedModelSerializer(serializers.ModelSerializer):
    def __new__(cls, *args, **kwargs):
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(meta, 'list_serializer_class', None)
        if not isinstance(list_serializer_class, EnhancedListSerializer.__class__):
            raise TypeError(
                f"In {cls.__name__}, to use EnhancedModelSerializer in Meta must declare: list_serializer_class = EnhancedListSerializer")
        return super().__new__(cls, *args, **kwargs)
        
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

class MetatableSerializer(EnhancedModelSerializer):
    class Meta:
        model = Metatable
        fields = '__all__'
        list_serializer_class = EnhancedListSerializer

class BranchSerializer(EnhancedModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'
        list_serializer_class = EnhancedListSerializer

class CalendarSerializer(EnhancedModelSerializer):
    class Meta:
        model = Calendar
        fields = '__all__'
        list_serializer_class = EnhancedListSerializer

class SettingSerializer(EnhancedModelSerializer):
    class Meta:
        model = Setting
        fields = '__all__'
        list_serializer_class = EnhancedListSerializer

class MyGroupSerializer(EnhancedModelSerializer):
    class Meta:
        model = MyGroup
        fields = '__all__'
        list_serializer_class = EnhancedListSerializer

class MyUserSerializer(EnhancedModelSerializer):
    class Meta:
        model = MyUser
        fields = '__all__'
        list_serializer_class = EnhancedListSerializer

class CourseSerializer(EnhancedModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Course
        fields = '__all__'
        list_serializer_class = EnhancedListSerializer

class UserRelatedField(serializers.RelatedField):
    def to_representation(self, obj):
        return {
            'name': obj.first_name + (' ' if obj.mid_name is None else ' ' + obj.mid_name + ' ') + obj.last_name,
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
    students = UserRelatedField(many=True, read_only=True)
    teacher = UserRelatedField(read_only=True)

    class Meta:
        model = ClassMetadata
        exclude = ('id', )
        list_serializer_class = EnhancedListSerializer

class ClassStudentSerializer(EnhancedModelSerializer):
    class Meta:
        model = ClassStudent
        fields = '__all__'
        list_serializer_class = EnhancedListSerializer

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
        list_serializer_class = EnhancedListSerializer

class AttendanceSerializer(EnhancedModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'
        list_serializer_class = EnhancedListSerializer

class LogSerializer(EnhancedModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'
        list_serializer_class = EnhancedListSerializer