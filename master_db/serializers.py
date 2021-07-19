from django.contrib.auth.models import Group

from rest_framework import serializers

from master_db.models import (
    Metatable, Branch, Calendar, CustomUser, Setting, Course,
    ClassMetadata, Schedule, Session, Log
)
from master_api.utils import validate_uuid4, prettyPrint


# For enhanced models
from collections import OrderedDict
from taggit_serializer.serializers import (
    TaggitSerializer, TagListSerializerField
)
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import _get_queryset

import json

# Enhanced models: Add excluding fields feature


def convertUUID(instance):
    dic = instance.__dict__
    retDict = dic.copy()
    for key in dic.keys():
        if len(key) > 3 and key[-3:] == '_id':
            newKey = key[:-3]
            value = getattr(instance, newKey)
            retDict[newKey] = str(value.uuid)
            retDict.pop(key)
    return OrderedDict(retDict)


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

    def is_valid(self, raise_exception=False):
        """
            Django's ModelSerializer does not support update without required
            fields. When super().is_valid is called it run_validation() its
            self.initial_data, so we just need to update and then return it
            to the original state. 

            Note: OrderedDict is a must for compatibility.
        """
        # Creation of an object is still fine
        if self.instance is None:
            return super().is_valid(raise_exception)
        temp = self.initial_data
        self.initial_data = convertUUID(self.instance)
        self.initial_data.update(temp)
        ret = super().is_valid(raise_exception)
        self.initial_data = temp
        return ret

    def exclude_field(self, field):
        try:
            self.fields.pop(field)
        except:
            raise KeyError(
                f"There is no `{field}` field in {self.__class__.__name__} to call exclude_field()")

        return self

    def exclude_created_updated(self):
        return self.exclude_field('created_at').exclude_field('updated_at')


MANY_RELATION_KWARGS = (
    'read_only', 'write_only', 'required', 'default', 'initial', 'source',
    'label', 'help_text', 'style', 'error_messages', 'allow_empty',
    'html_cutoff', 'html_cutoff_text'
)


class UUIDRelatedField(serializers.RelatedField):
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Invalid uuid "{uuid_value}" - object does not exist.'),
        'incorrect_type': _('Incorrect type. Expected uuid value, received {data_type}.'),
        'invalid_uuid': _('{message}')
    }

    def __init__(self, model, *args, **kwargs):
        kwargs['queryset'] = _get_queryset(model)
        super().__init__(*args, **kwargs)

    @classmethod
    def many_init(cls, *args, **kwargs):
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs:
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return UUIDManyRelatedField(**list_kwargs)

    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            if isinstance(data, bool):
                raise TypeError
            return queryset.get(uuid=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', uuid_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)
        except ValidationError as message:
            self.fail('invalid_uuid', message=message)

    def to_representation(self, value):
        return value.uuid


class UUIDManyRelatedField(serializers.ManyRelatedField):
    default_error_messages = {
        'not_a_list': _(
            'Expected a list of items but got type "{input_type}".'),
        'invalid_json': _("Invalid json list. A {name} list submitted in string"
                          " form must be valid json."),
        'not_a_str': _('All list items must be of string type.'),
        'invalid': _('“%(value)s” is not a valid UUID.'),
    }

    def to_internal_value(self, value):
        if not value:
            value = "[]"
        else:
            # When passing data=request.data param comes in
            # list with a single string(data sent)
            value = value[0] if isinstance(value, list) else value
        try:
            value = json.loads(value)
        except ValueError:
            self.fail('invalid_json',
                      name=self.child_relation.__class__.__name__)

        if not isinstance(value, list):
            self.fail('not_a_list', input_type=type(value).__name__)

        for s in value:
            if not validate_uuid4(s):
                raise ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': value},
                )
            yield self.child_relation.to_internal_value(s)


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


class CustomUserSerializer(EnhancedModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class CourseSerializer(TaggitSerializer, EnhancedModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Course
        exclude = ('id',)


class UserRelatedField(UUIDRelatedField):
    def __init__(self, *args, **kwargs):
        super().__init__(CustomUser, *args, **kwargs)

    def to_representation(self, obj):
        return {
            'name': obj.first_name + ' ' + obj.last_name,
            'mobile': obj.mobile,
            'email': obj.email,
            'uuid': obj.uuid,
        }


class CourseRelatedField(UUIDRelatedField):
    def __init__(self, *args, **kwargs):
        super().__init__(Course, *args, **kwargs)

    def to_representation(self, obj):
        return {
            'name': obj.name,
            'uuid': obj.uuid,
        }


class ClassMetadataSerializer(EnhancedModelSerializer):
    course = CourseRelatedField()
    students = UserRelatedField(many=True)
    teacher = UserRelatedField()

    class Meta:
        model = ClassMetadata
        exclude = ('id', )


class ClassRelatedField(UUIDRelatedField):
    def __init__(self, *args, **kwargs):
        super().__init__(ClassMetadata, *args, **kwargs)

    def to_representation(self, obj):
        return {
            'name': obj.name,
            'course': obj.course.name,
            'uuid': obj.uuid,
        }


class ScheduleSerializer(EnhancedModelSerializer):
    classroom = ClassRelatedField()

    class Meta:
        model = Schedule
        fields = '__all__'


class ScheduleRelatedField(UUIDRelatedField):
    def __init__(self, *args, **kwargs):
        super().__init__(Schedule, *args, **kwargs)

    def to_representation(self, obj):
        return ScheduleSerializer(obj).exclude_created_updated().data


class SessionSerializer(EnhancedModelSerializer):
    student = UserRelatedField()
    session = ScheduleRelatedField()

    class Meta:
        model = Session
        exclude = ('id', )


class LogSerializer(EnhancedModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'
