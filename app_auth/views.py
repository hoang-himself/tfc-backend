from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password, check_password

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

from master_db.models import (
    Metatable, Branch, Setting, Role, Course,
    ClassMetadata, ClassStudent, ClassTeacher, Session, Attendance, Log
)
from master_db.serializers import (
    MetatableSerializer, BranchSerializer, SettingSerializer, RoleSerializer, UserSerializer, CourseSerializer,
    ClassMetadataSerializer, ClassMetadataSerializer, ClassMetadataSerializer, SessionSerializer, AttendanceSerializer, LogSerializer
)

import datetime
import jwt


def __get_setting_session(request):
    if request.session.get('setting', -1) != -1:
        request.session.set('setting', SettingSerializer(
            Setting.objects.all(), many=True).data)


def __generate_access_token(user):
    access_token_payload = {
        'aud': user.get("id"),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=15),
        'iat': datetime.datetime.utcnow(),
    }

    access_token = jwt.encode(access_token_payload,
                              settings.SECRET_KEY,
                              algorithm='HS256').decode('utf-8')
    return access_token


def __generate_refresh_token(user):
    refresh_token_payload = {
        'aud': user.get("id"),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=14),
        'iat': datetime.datetime.utcnow()
    }
    refresh_token = jwt.encode(refresh_token_payload,
                               settings.REFRESH_TOKEN_SECRET,
                               algorithm='HS256').decode('utf-8')
    return refresh_token


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    response = Response()
    response.status_code = status.HTTP_400_BAD_REQUEST
    response.data = {
        "result": "error",
        "errors": [
            {
                "status": 400,
                "title": "validation_exception",
                "detail": "",
                "context": None
            }
        ]
    }

    email = request.POST.get('email')
    password = request.POST.get('password')

    if email is None:
        response.data['errors'][0]['detail'] = "Error validating email: The property email is required"
        return response
    elif password is None:
        response.data['errors'][0]['detail'] = "Error validating password: The property password is required"
        return response
    elif email == '':
        response.data['errors'][0]['detail'] = "Error validating email: Must be at least 1 character long"
        return response
    elif password == '':
        response.data['errors'][0]['detail'] = "Error validating password: Must be at least 1 character long"
        return response

    true_user = get_user_model().objects.filter(email=email).first()
    if(true_user is None):
        response.data['errors'][0]['detail'] = "Error validating email: Email not found"
        return response

    true_user = UserSerializer(true_user).data
    if not check_password(password, true_user.get("password")):
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            "result": "error",
            "errors": [
                {
                    "status": 400,
                    "title": "validation_exception",
                    "detail": "",
                    "context": None
                }
            ]
        }

    del true_user['id']
    del true_user['password']

    access_token = __generate_access_token(true_user)
    refresh_token = __generate_refresh_token(true_user)

    response.set_cookie(key='refresh', value=refresh_token, httponly=True)
    response.status_code = status.HTTP_202_ACCEPTED
    response.data = {
        "result": "ok",
        "token": {
            "access": access_token,
            "refresh": refresh_token
        }
    }
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def check(request):
    pass


@api_view(['DELETE'])
@permission_classes([AllowAny])
def logout(request):
    """
    ! Should not work with JWT since JWT is stateless.
    ! Maybe add generated token to a database with TTL
    """
    response = Response()

    try:
        # simply delete the token to force a login
        request.user.auth_token.delete()
    except (AttributeError, ObjectDoesNotExist):
        pass

    response.status = status.HTTP_204_NO_CONTENT
    response.data = {
        "message": "Logged out",
        "details": {}
    }

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh(request):
    pass
