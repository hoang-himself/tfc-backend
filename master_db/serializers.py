from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group

from rest_framework import serializers

from master_db.models import (
    Metatable, Branch, Calendar, CustomUser, Setting, Course,
    ClassMetadata, Schedule, Session, Log, TemplateBase
)
from master_db import models
from master_api.utils import validate_uuid4, prettyPrint


# For custom classes
from collections import OrderedDict
from taggit_serializer.serializers import (
    TaggitSerializer, TagListSerializerField
)
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import _get_queryset

from rest_framework.fields import empty

import json


"""
    * Enhanced serializer: Include new and improve already existing 
    * features
        + ignore in class Meta: ignore fields when calling .data
        + ignore_field: dynamically add fields to ignore
        + clear_ignore: reset ignore to its original state
        + list_serializer_class: Automatically set to
        EnhancedListSerializer for further customization
        + Update ignore required fields: Updating models now does
        not need required fields, ie. name is required in Course
        but when update we don't specify name so an error will be
        raised, Enhanced serializer resolves this.
        + editable=False in model will not be modified: resolve
        https://github.com/encode/django-rest-framework/issues/1604
        + TemplateBase: to use this serializer the model's metaclass
        must be TemplateBase or its subclass.
"""


class EnhancedListSerializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(self.child, EnhancedModelSerializer):
            raise TypeError(
                f"To use EnhancedListSerializer, {self.child.__class__.__name__}"
                " must be EnhancedModelSerializer or its subclass")

    def ignore_field(self, field):
        self.child.ignore_field(field)
        return self

    def clear_ignore(self):
        self.child.clear_ignore()


class EnhancedModelSerializer(serializers.ModelSerializer):
    def __new__(cls, *args, **kwargs):
        meta = getattr(cls, 'Meta', None)
        if not issubclass(meta.model.__class__, TemplateBase):
            raise TypeError(
                f"In {cls.__name__}, metaclass {meta.model.__name__} must be"
                " TemplateBase or its subclass")
        if not hasattr(meta, 'list_serializer_class'):
            setattr(meta, 'list_serializer_class', EnhancedListSerializer)
        elif not issubclass(meta.list_serializer_class, EnhancedListSerializer):
            raise TypeError(
                f"In {cls.__name__}, list_serializer_class must be "
                "EnhancedListSerializer or its subclass")

        return super().__new__(cls, *args, **kwargs)

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self._ignore = self.Meta.ignore if hasattr(
            self.Meta, 'ignore') else tuple()
        self.ignore = {}
        for field in self._ignore:
            self.ignore_field(field)

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

        temp = self.initial_data
        self.initial_data = convertUUID(self.instance)
        self.initial_data.update(temp)
        ret = super().is_valid(raise_exception)
        self.initial_data = temp
        return ret

    @property
    def _writable_fields(self):
        for name, field in self.fields.items():
            if self.instance:
                model_editable = self.Meta.model.editable_fields.get(
                    name, True)
            else:
                model_editable = True
            if not field.read_only and model_editable:
                yield field

    @property
    def _readable_fields(self):
        for name, field in self.fields.items():
            ignore = self.ignore.get(name, False)
            if not field.write_only and not ignore:
                yield field

    def ignore_field(self, field):
        """
            Ignore field when calling .data
        """
        if not field in self.fields:
            raise KeyError(
                f"There is no `{field}` field in {self.__class__.__name__} "
                "to ignore")
        if field in self.ignore.keys():
            return self
        else:
            self.ignore[field] = True
        # Reset .data calling when ignore is modified
        if hasattr(self, '_data'):
            delattr(self, '_data')

        return self

    def clear_ignore(self):
        """
            Reset ignore to the first ignored in class Meta
        """
        if hasattr(self, '_data'):
            delattr(self, '_data')
        self.ignore = dict.fromkeys(self._ignore, True)


MANY_RELATION_KWARGS = (
    'read_only', 'write_only', 'required', 'default', 'initial', 'source',
    'label', 'help_text', 'style', 'error_messages', 'allow_empty',
    'html_cutoff', 'html_cutoff_text'
)

"""
    * UUID Related Field: An alternative to PrimaryKeyRelatedField,
    * but instead of pk we use uuid with model's UUIDField
        + Writting relation fields now requires uuid instead of id
        + Many-to-many now take in a list of uuids in form of json
        format: list = '["elem1", "elem2", "elem3"]'
        + ModelRelatedField naming: When naming a custom related
        field, it is recommend to name the field with the name of
        the corresponding model in master_db.model, or else
        queryset will not be set. 
"""


class FieldMetaclass(type):
    def __new__(cls, name, bases, attrs):
        model = getattr(models, name.replace('RelatedField', ''), None)
        if model is not None:
            attrs['queryset'] = _get_queryset(model)
        return super().__new__(cls, name, bases, attrs)


class UUIDRelatedField(serializers.RelatedField, metaclass=FieldMetaclass):
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Invalid uuid "{uuid_value}" - object does not exist.'),
        'incorrect_type': _('Incorrect type. Expected uuid value, received {data_type}.'),
        'invalid_uuid': _('“{value}” is not a valid UUID.'),
    }

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
        except ValidationError:
            self.fail('invalid_uuid', value=data)

    def to_representation(self, value):
        return value.uuid


class UUIDManyRelatedField(serializers.ManyRelatedField):
    default_error_messages = {
        'not_a_list': _(
            'Expected a list of items but got type "{input_type}".'),
        'invalid_json': _("Invalid json list. A {name} list submitted in string"
                          " form must be valid json."),
        'not_a_str': _('All list items must be of string type.'),
        'invalid_uuid': _('“{value}” is not a valid UUID.'),
    }

    def to_internal_value(self, value):
        if not value:
            value = "[]"
        elif isinstance(value, list) and len(value) == 1:
            # ! Naive resolve
            # When passing data=request.data param comes in
            # list with a single string(data sent).
            # May be due to OrderedDict
            value = value[0]
        try:
            value = json.loads(value)
        except ValueError:
            self.fail('invalid_json',
                      name=self.child_relation.__class__.__name__)

        if not isinstance(value, list):
            self.fail('not_a_list', input_type=type(value).__name__)

        for s in value:
            if not validate_uuid4(s):
                self.fail('invalid_uuid', value=value)
            yield self.child_relation.to_internal_value(s)


class MetatableSerializer(EnhancedModelSerializer):
    class Meta:
        model = Metatable
        exclude = ('id', )


class BranchSerializer(EnhancedModelSerializer):
    class Meta:
        model = Branch
        exclude = ('id', )


class CalendarSerializer(EnhancedModelSerializer):
    class Meta:
        model = Calendar
        exclude = ('id', )


class SettingSerializer(EnhancedModelSerializer):
    class Meta:
        model = Setting
        exclude = ('id', )


class CustomUserSerializer(EnhancedModelSerializer):
    class Meta:
        model = CustomUser
        exclude = ('id', )

    def validate_password(self, password):
        return make_password(password)


class CourseSerializer(TaggitSerializer, EnhancedModelSerializer):
    tags = TagListSerializerField()

    class Meta:
        model = Course
        exclude = ('id', )


class CustomUserRelatedField(UUIDRelatedField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_representation(self, obj):
        return {
            'name': obj.first_name + ' ' + obj.last_name,
            'mobile': obj.mobile,
            'email': obj.email,
            'uuid': obj.uuid,
        }


class CourseRelatedField(UUIDRelatedField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_representation(self, obj):
        return {
            'name': obj.name,
            'uuid': obj.uuid,
        }


class ClassMetadataSerializer(EnhancedModelSerializer):
    course = CourseRelatedField()
    students = CustomUserRelatedField(many=True)
    teacher = CustomUserRelatedField()

    class Meta:
        model = ClassMetadata
        exclude = ('id', )


class ClassMetadataRelatedField(UUIDRelatedField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_representation(self, obj):
        return {
            'name': obj.name,
            'course': obj.course.name,
            'uuid': obj.uuid,
        }


class ScheduleSerializer(EnhancedModelSerializer):
    classroom = ClassMetadataRelatedField()

    class Meta:
        model = Schedule
        exclude = ('id', )


class ScheduleRelatedField(UUIDRelatedField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_representation(self, obj):
        return {
            'uuid': obj.uuid,
            'time_start': obj.time_start,
            'time_end': obj.time_end,
        }


class SessionSerializer(EnhancedModelSerializer):
    schedule = ScheduleRelatedField()
    student = CustomUserRelatedField()

    class Meta:
        model = Session
        exclude = ('id', )


class LogSerializer(EnhancedModelSerializer):
    class Meta:
        model = Log
        exclude = ('id', )
