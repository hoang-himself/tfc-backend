from django.contrib.auth import get_user_model

from rest_framework import (exceptions, status)
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from master_api.utils import (get_by_uuid, convert_primitive)
from master_db import (models, serializers)

CustomUser = get_user_model()

SERIALIZERS = {
    models.Course: serializers.CourseSerializer,
    models.ClassMetadata: serializers.ClassMetadataSerializer,
    models.Schedule: serializers.ScheduleSerializer,
    models.Session: serializers.SessionSerializer,
    CustomUser: serializers.CustomUserSerializer,
}

CREATE_RESPONSE = {'data': 'Ok', 'status': status.HTTP_201_CREATED}

EDIT_RESPONSE = {'data': 'Ok', 'status': status.HTTP_200_OK}

DELETE_RESPONSE = {'data': 'Deleted', 'status': status.HTTP_200_OK}

GET_RESPONSE = {'status': status.HTTP_200_OK}

LIST_RESPONSE = {'status': status.HTTP_200_OK}


def create_object(model, **kwargs):
    try:
        data = kwargs.pop('data')
    except KeyError:
        raise KeyError('Payload cannot be empty')
    Serializer = SERIALIZERS[model]
    serializer = Serializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(**CREATE_RESPONSE)
    else:
        raise exceptions.ParseError(convert_primitive(serializer.errors))


def edit_object(model, **kwargs):
    try:
        data = kwargs.pop('data').copy()
    except KeyError:
        raise KeyError('Payload cannot be empty')
    Serializer = SERIALIZERS[model]
    uuid = uuid[0] if isinstance(uuid := data.pop('uuid', None), list) else uuid
    instance = get_by_uuid(model, uuid)
    serializer = Serializer(instance=instance, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(**EDIT_RESPONSE)
    else:
        raise exceptions.ParseError(convert_primitive(serializer.errors))


def get_object(model, **kwargs):
    try:
        data = kwargs.pop('data')
    except KeyError:
        raise KeyError('Payload cannot be empty')
    try:
        uuid = data['uuid']
    except KeyError:
        raise exceptions.ParseError({'uuid': 'This field is required.'})
    Serializer = SERIALIZERS[model]
    return Response(Serializer(get_by_uuid(model, uuid)).data)


def delete_object(model, **kwargs):
    try:
        data = kwargs.pop('data')
    except KeyError:
        raise KeyError('Payload cannot be empty')
    try:
        uuid = data['uuid']
    except KeyError:
        raise exceptions.ParseError({'uuid': 'This field is required.'})
    get_by_uuid(model, uuid).delete()
    return Response(**DELETE_RESPONSE)


@api_view(['POST', 'GET', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def ping(request):
    return Response(data={'detail': 'pong'}, status=status.HTTP_200_OK)
