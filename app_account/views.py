from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_protect

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app_auth.utils import request_to_userobj
from master_db.serializers import CustomUserSerializer
from master_api.views import (create_object, edit_object,
                              delete_object, get_object)

import datetime
import re

CustomUser = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def get_self(request):
    user = request_to_userobj(request)
    return Response(data=CustomUserSerializer(user).data)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def create_user(request):
    return create_object(CustomUser, data=request.data)


@api_view(['PATCH'])
@permission_classes([AllowAny])
@csrf_protect
def edit_user(request):
    return edit_object(CustomUser, data=request.data)


@api_view(['DELETE'])
@permission_classes([AllowAny])
@csrf_protect
def delete_user(request):
    # TODO
    pass


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def list_user(request):
    return Response(
        CustomUserSerializer(
            CustomUser.objects.all(), many=True).data
    )


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def list_staff(request):
    # TODO
    pass


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def create_staff(request):
    """
        Return list of users with a specified view
    """
    # TODO
    filter_query = request.GET.getlist('filter')

    if not filter_query:
        filter_query = [
            'uuid',
            'email',
            'first_name',
            'last_name',
            'birth_date',
            'mobile',
            'male',
            'address',
            'is_active',
            'last_login',
            'date_joined',
            'date_updated',
        ]

    filter_dict = {
        'uuid': True,
        'email': True,
        'first_name': True,
        'last_name': True,
        'birth_date': True,
        'mobile': True,
        'male': True,
        'address': True,
        'avatar': False,
        'date_joined': True,
        # 'role__name': True,
        'is_active': True,
        'last_login': True,
        'date_joined': True,
        'date_updated': True,
    }

    # TODO
    listZ = []
    for key in filter_query:  # Query filter for choosing views
        if filter_dict[key]:
            listZ.append(key)

    # Asterisk expands list into separated args
    # https://docs.python.org/2/tutorial/controlflow.html#unpacking-argument-lists
    data = CustomUser.objects.all().values(*listZ)
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def edit_staff(request):
    # TODO
    pass


@api_view(['DELETE'])
@permission_classes([AllowAny])
@csrf_protect
def delete_staff(request):
    # TODO
    pass
