from rest_framework.exceptions import NotFound, ParseError
from django.core.exceptions import ValidationError

def formdata_bool(var):
    # Null for boolean
    if var is None or var == '':
        return None

    low = var.lower().strip()
    if low == 'true':
        return True
    if low == 'false':
        return False
    
    raise ParseError('Boolean value must be `true` or `false` after being lowered')

def _get_queryset(klass):
    """
    Return a QuerySet or a Manager.
    Duck typing in action: any class with a `get()` method (for
    get_object_or_404) or a `filter()` method (for get_list_or_404) might do
    the job.
    """
    # If it is a model class or anything else with ._default_manager
    if hasattr(klass, '_default_manager'):
        return klass._default_manager.all()
    return klass


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
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise NotFound(f'{name_print} does not exist')
    
def model_full_clean(model):
    try:
        model.full_clean()
    except ValidationError as message:
        raise ParseError(dict(message))
    
def edit_object(model, modifiedDict, modifiedList, avoid=[]):
    for key, value in modifiedDict.items():
        if hasattr(model, key) and value != getattr(model, key) and not key in avoid:
            setattr(model, key, value)
            modifiedList.append(key)
    


def get_list_or_404(klass, name_print, *args, **kwargs):
    """
    Use filter() to return a list of objects, or raise a Http404 exception if
    the list is empty.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the filter() query.
    """
    queryset = _get_queryset(klass)
    if not hasattr(queryset, 'filter'):
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_list_or_404() must be a Model, Manager, or "
            "QuerySet, not '%s'." % klass__name
        )
    obj_list = list(queryset.filter(*args, **kwargs))
    if not obj_list:
        raise NotFound(f'{name_print} does not exist')
    return obj_list

def get_queryset(klass, *args, **kwargs):
    """
    Use filter() to return a list of objects.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the filter() query.
    """
    queryset = _get_queryset(klass)
    if not hasattr(queryset, 'filter'):
        klass__name = klass.__name__ if isinstance(klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_queryset() must be a Model, Manager, or "
            "QuerySet, not '%s'." % klass__name
        )
    return queryset.filter(*args, **kwargs)
