from django.core.exceptions import ValidationError
from django.shortcuts import _get_queryset
from rest_framework.exceptions import NotFound, ParseError

import uuid
import datetime
import json


def convert_json_list(target):
    try:
        return json.loads(target)
    except ValueError:
        raise ParseError({'invalid_list': 'List must be in json format'})


def convert_time(s, format_time='%Y-%m-%d %H:%M'):
    return datetime.datetime.strptime(s, format_time).astimezone()


def validate_uuid4(value):
    if value is not None and not isinstance(value, uuid.UUID):
        input_form = 'int' if isinstance(value, int) else 'hex'
        try:
            uuid.UUID(**{input_form: value})
        except (AttributeError, ValueError):
            return False
    return True


def formdata_bool(var: str):
    # Null for boolean
    if var is None or var == '':
        return None

    low = var.lower().strip()
    if low == 'true':
        return True
    if low == 'false':
        return False

    raise ParseError(
        'Boolean value must be `true` or `false` after being lowered'
    )


def get_object_or_404(klass, name_print=None, *args, **kwargs):
    """
    Use get() to return an object, or raise a Http404 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Like with QuerySet.get(), MultipleObjectsReturned is raised if more than
    one object is found.
    """
    queryset = _get_queryset(klass)
    name_print = name_print if name_print is not None else klass.__name__
    if not hasattr(queryset, 'get'):
        klass__name = klass.__name__ if isinstance(
            klass, type
        ) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise NotFound(f'{name_print} does not exist')


def get_by_uuid(klass, uuid):
    """
    Get object by uuid using get_object_or_404 with additional
    error handling (invalid uuid)
    """
    try:
        return get_object_or_404(klass, uuid=uuid)
    except ValidationError as message:
        raise ParseError({'detail': list(message)})


def get_list_by_uuid(klass, uuid):
    """
    Get list of objects by uuid using get_object_or_404 with
    additional error handling (invalid uuid)
    """
    try:
        return get_list_or_404(klass, uuid=uuid)
    except ValidationError as message:
        raise ParseError({'detail': list(message)})


def get_list_or_404(klass, name_print, *args, **kwargs):
    """
    Use filter() to return a list of objects, or raise a Http404 exception if
    the list is empty.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the filter() query.
    """
    queryset = _get_queryset(klass)
    if not hasattr(queryset, 'filter'):
        klass__name = klass.__name__ if isinstance(
            klass, type
        ) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_list_or_404() must be a Model, Manager, or "
            "QuerySet, not '%s'." % klass__name
        )
    obj_list = list(queryset.filter(*args, **kwargs))
    if not obj_list:
        raise NotFound(f'{name_print} does not exist')
    return obj_list


# For django test
def compare_dict(obj, dict1, dict2):
    """
        Compare every key in dict1 to that of dict2. This means if
        dict2 has keys that are not in dict1, it will not be checked.
    """
    for key, value in dict1.items():
        if isinstance(value, list):
            value = set(value)
            dict2[key] = set(dict2[key])
        if isinstance(dict2[key], dict):
            dict2[key] = str(dict2[key]['uuid'])

        obj.assertTrue(
            value == dict2[key],
            msg=f"{key}: {value} <-> {dict2[key]} => {value == dict2[key]}"
        )


def convert_primitive(elem):
    """
        Django response often be OrderedDict or QuerySet so we
        should convert every element to python dict and list.

        If an element is neither a dict nor list it will be
        converted to string.

        Single quote (') in a string will be converted to back
        quote (`) for better visualization
    """
    klass = elem.__class__
    if issubclass(klass, list) or \
        issubclass(klass, tuple) or \
            issubclass(klass, set):
        elem = list(elem)
        for i in range(len(elem)):
            elem[i] = convert_primitive(elem[i])
    elif issubclass(klass, dict):
        elem = dict(elem)
        for key in elem.keys():
            elem[key] = convert_primitive(elem[key])
    else:
        elem = str(elem).replace('\'', '`')
    return elem


def prettyStr(text, indentOffset=2):
    """
        Convert an object after convert_primitive() to a string
        with better visualization
    """
    def reverse_bracket(bracket):
        if bracket == '{':
            return '}'
        elif bracket == '}':
            return '{'
        elif bracket == '[':
            return ']'
        elif bracket == ']':
            return '['

    subtext = text = str(convert_primitive(text))
    indent = char = 0
    bracket = []
    ignore = False
    for i in range(len(text)):
        if text[i] == '\'':
            ignore = not ignore
        if ignore:
            continue
        if text[i] == '{' or text[i] == '[':
            if text[i + 1] == reverse_bracket(text[i]):
                i = i + 2
                continue
            bracket.append(text[i])
            indent += indentOffset
            offset = i + char
            subtext = subtext[:offset+1] + \
                f"\n{' '*indent}" + subtext[offset+1:]
            char += indent + 1
        elif text[i] == '}' or text[i] == ']':
            if bracket[-1] == reverse_bracket(text[i]):
                bracket.pop()
                indent -= indentOffset
                offset = i + char
                subtext = subtext[:offset] + \
                    f"\n{' '*indent}" + subtext[offset:]
                char += indent + 1
        elif text[i] == ',':
            offset = i + char
            if text[i + 1] == ' ':
                subtext = subtext[:offset + 1] + subtext[offset + 2:]
                char -= 1
            subtext = subtext[:offset+1] + \
                f"\n{' '*indent}" + subtext[offset+1:]
            char += indent + 1

    return "\n" + subtext


def prettyPrint(text):
    print(prettyStr(text))
