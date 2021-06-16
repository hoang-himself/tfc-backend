from os import access
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect

from master_db.models import (
    Metatable, Branch, Setting, Role, Course,
    ClassMetadata, ClassStudent, ClassTeacher, Session, Attendance, Log
)
from master_db.serializers import (
    MetatableSerializer, BranchSerializer, SettingSerializer, RoleSerializer, UserSerializer, CourseSerializer,
    ClassMetadataSerializer, ClassMetadataSerializer, ClassMetadataSerializer, SessionSerializer, AttendanceSerializer, LogSerializer
)
from .utils import (
    generate_access_token,
    generate_refresh_token, get_setting_session
)

import datetime
import jwt


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login(request):
    response = Response()
    response.status_code = status.HTTP_400_BAD_REQUEST
    User = get_user_model()
    valid = 1
    errors = []

    email = request.POST.get('email')
    password = request.POST.get('password')

    if (email is None or email == ''):
        errors.append(
            {
                "email": "this field is required"
            }
        )
        valid -= 1
    if (password is None or password == ''):
        errors.append(
            {
                "password": "this field is required"
            }
        )
        valid -= 1
    if (valid < 1):
        response.data = {
            "result": "error",
            "errors": errors
        }
        return response

    user = User.objects.filter(email=email).first()
    if (user is None):
        response.data = {
            "result": "error",
            "errors": [
                {
                    "email": "not found"
                },
            ]
        }
        return response

    user = UserSerializer(user).data
    if not check_password(password, user.get("password")):
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            "result": "error",
            "errors": [
                {
                    "password": "no match"
                },
            ]
        }
        return response

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
    response.status_code = status.HTTP_200_OK
    response.data = {
        "result": "ok",
        "token": {
            "access": access_token,
        },
    }
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def check(request):
    pass


@api_view(['DELETE'])
@permission_classes([AllowAny])
def logout(request):
    pass


@api_view(['POST'])
@permission_classes([AllowAny])
# @csrf_protect
def refresh(request):
    response = Response()
    User = get_user_model()

    refresh_token = request.COOKIES.get('refreshtoken')
    if (refresh_token is None):
        response.status_code = status.HTTP_403_FORBIDDEN
        response.data = {
            "result": "error",
            "errors": [
                {
                    "refresh token not found"
                },
            ]
        }
        return response

    try:
        payload = jwt.decode(
            refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {
            "result": "error",
            "errors": [
                {
                    "refresh token expired"
                },
            ]
        }
        return response
    except jwt.InvalidSignatureError:
        response.status_code = status.HTTP_403_FORBIDDEN
        response.data = {
            "result": "error",
            "errors": [
                {
                    "invalid refresh token"
                },
            ]
        }
        return response

    user = User.objects.filter(username=payload.get('user_id')).first()
    if (user is None):
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            "result": "error",
            "errors": [
                {
                    "user not found"
                },
            ]
        }
        return response
    if not (user.is_active):
        response.status_code = status.HTTP_403_FORBIDDEN
        response.data = {
            "result": "error",
            "errors": [
                {
                    "user is inactive"
                },
            ]
        }
        return response

    user = UserSerializer(user).data
    access_token = generate_access_token(user)
    response.status_code = status.HTTP_200_OK
    response.data = {
        "result": "ok",
        "token": [
            {
                "access": access_token
            },
        ]
    }
    return response
