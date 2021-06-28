from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes


from app_auth.utils import has_perm
from master_db.models import MyUser, ClassMetadata, Course, ClassStudent, ClassTeacher
from master_db.serializers import MyUserSerializer

import re
import datetime
import json
import jwt


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def list_class(request):
    """
        Return list of classes with a specified view
    """
    check = has_perm(request, ['account_cred'])
    if check.status_code >= 400:
        return check

    filter_query = request.GET.getlist('filter')

    if not filter_query:
        filter_query = [
            'course',
            'name',
            'status',
            'created_at',
            'updated_at'
        ]

    filter_dict = {
        'course': True,
        'name': True,
        'status': True,
        'created_at': True,
        'updated_at': True
    }

    listZ = []
    for key in filter_query:  # Query filter for choosing views
        if filter_dict[key]:
            listZ.append(key)

    # Asterisk expands list into separated args
    # https://docs.python.org/2/tutorial/controlflow.html#unpacking-argument-lists
    data = ClassMetadata.objects.all().values(*listZ)
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def list_user(request, class_name):
    """
        Return list of users with a specified view
    """
    check = has_perm(request, ['account_cred'])
    if check.status_code >= 400:
        return check

    class_obj = get_object_or_404(ClassMetadata, name=class_name)
    filter_query = request.GET.getlist('filter')

    if not filter_query:
        filter_query = [
            'uuid',
            'username',
            'first_name',
            'mid_name',
            'last_name',
            'email',
            'birth_date',
            'mobile',
            'male',
            'address',
            'role__name',
            'is_active',
            'created_at',
            'updated_at'
        ]

    filter_dict = {
        'uuid': True,
        'username': True,
        'first_name': True,
        'mid_name': True,
        'last_name': True,
        'email': True,
        'password': False,
        'birth_date': True,
        'mobile': True,
        'male': True,
        'address': True,
        'avatar': False,
        'role__name': True,
        'is_active': True,
        'created_at': True,
        'updated_at': True
    }

    listZ = []
    for key in filter_query:  # Query filter for choosing views
        if filter_dict[key]:
            listZ.append(key)

    students = class_obj.classstudent_set
    teachers = class_obj.classteacher_set

    # Asterisk expands list into separated args
    # https://docs.python.org/2/tutorial/controlflow.html#unpacking-argument-lists
    data = teachers.objects.all().values(*listZ)
    data.update(students.objects.all().values(*listZ))
    return Response(data)
