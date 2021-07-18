from django.db.models.query_utils import subclasses
from rest_framework.exceptions import NotFound, ParseError
from django.core.exceptions import ValidationError
from django.shortcuts import _get_queryset

import json
import pprint


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
        'Boolean value must be `true` or `false` after being lowered')


def get_object_or_404(klass, name_print, *args, **kwargs):
    """
    Use get() to return an object, or raise a Http404 exception if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Like with QuerySet.get(), MultipleObjectsReturned is raised if more than
    one object is found.
    """
    queryset = _get_queryset(klass)
    if not hasattr(queryset, 'get'):
        klass__name = klass.__name__ if isinstance(
            klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise NotFound(f'{name_print} does not exist')


def get_by_uuid(klass, name_print, uuid):
    """
    Get object by uuid using get_object_or_404 with additional 
    error handling (invalid uuid)
    """
    try:
        return get_object_or_404(klass, name_print, uuid=uuid)
    except ValidationError as message:
        raise ParseError({'detail': list(message)})


def model_full_clean(model):
    try:
        model.full_clean()
    except ValidationError as message:
        raise ParseError(dict(message))


def edit_object(model, modifiedDict, avoid=None):
    modifiedList = []
    avoid = avoid if avoid is not None else []
    for key, value in modifiedDict.items():
        if hasattr(model, key) and value != getattr(model, key) and not key in avoid:
            setattr(model, key, value)
            modifiedList.append(key)

    return modifiedList


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
            klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_list_or_404() must be a Model, Manager, or "
            "QuerySet, not '%s'." % klass__name
        )
    obj_list = list(queryset.filter(*args, **kwargs))
    if not obj_list:
        raise NotFound(f'{name_print} does not exist')
    return obj_list


# For django test
def prettyPrint(text):
    def convert_every_elem(elem):
        """
            Django response often be OrderedDict or QuerySet so we
            should convert every element to python dict and list.
            
            If an element is neither a dict nor list it will be 
            converted to string.
        """
        if issubclass(elem.__class__, list):
            elem = list(elem)
            for i in range(len(elem)):
                elem[i] = convert_every_elem(elem[i])
        elif issubclass(elem.__class__, dict):
            elem = dict(elem)
            for key in elem.keys():
                elem[key] = convert_every_elem(elem[key])
        else:
            elem = str(elem)
        return elem
    
    text = str(convert_every_elem(text))
    
    subtext = text
    indent = 0
    bracket = []
    char = 0
    for i in range(len(text)):
        if text[i] == '{' or text[i] == '[':
            bracket.append(text[i])
            indent += 2
            offset = i + char
            subtext = subtext[:offset+1] + \
                f"\n{' '*indent}" + subtext[offset+1:]
            char += indent + 1

        if text[i] == '}' or text[i] == ']':
            if (text[i] == '}' and bracket[-1] == '{') or (text[i] == ']' and bracket[-1] == '['):
                bracket.pop()
                indent -= 2
                offset = i + char
                subtext = subtext[:offset] + \
                    f"\n{' '*indent}" + subtext[offset:]
                char += indent + 1

        if text[i] == ',':
            offset = i + char

            if text[i + 1] == ' ':
                subtext = subtext[:offset+1] + subtext[offset+2:]
                char -= 1
            subtext = subtext[:offset+1] + \
                f"\n{' '*indent}" + subtext[offset+1:]
            char += indent + 1

    print(subtext)
