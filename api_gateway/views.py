from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password, check_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

from database_app.models import *
from .serializers import *

import datetime
import jwt


def __get_setting_session(request):
    if request.session.get('setting', -1) != -1:
        request.session.set('setting', SettingSerializer(
            setting.objects.all(), many=True).data)


def __generate_access_token(user):
    access_token_payload = {
        'user_id': user.get("user_id"),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, minutes=5),
        'iat': datetime.datetime.utcnow(),
    }

    '''
    Upstream bug
    Use simpleJWT==4.5.0 and PyJWT==1.7.1 as workaround
    '''
    access_token = jwt.encode(access_token_payload,
                              settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
    return access_token


def __generate_refresh_token(user):
    refresh_token_payload = {
        'user_id': user.get("user_id"),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    refresh_token = jwt.encode(
        refresh_token_payload, settings.REFRESH_TOKEN_SECRET, algorithm='HS256').decode('utf-8')

    return refresh_token


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([AllowAny])
def test(request):
    response = Response()

    response.status = status.HTTP_200_OK
    response.data = {
        "message": "OK",
        "details": {
            "METHOD": request.method,
            "ready": {
                "api/test",
                "api/login"
            }
        }
    }

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    if email is None or password is None:
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={
                            "message": "Invalid payload",
                            "details": {
                                "email": "This field is required",
                                "password": "This field is required"
                            }
                        }
                        )

    true_user = user.objects.filter(user_email=email).first()
    if(true_user is None):
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={
                            "message": "Invalid payload",
                            "details": {
                                "email": "Email not found",
                                "password": ""
                            }
                        }
                        )

    true_user = UserSerializer(true_user).data

    if not check_password(password, true_user.get("user_password")):
        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={
                            "message": "Invalid payload",
                            "details": {
                                "email": "",
                                "password": "Bad password"
                            }
                        }
                        )

    del true_user['user_id']
    del true_user['user_password']

    access_token = __generate_access_token(true_user)
    refresh_token = __generate_refresh_token(true_user)

    response = Response()
    response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
    response.status = status.HTTP_202_ACCEPTED
    response.data = {
        "message": "OK",
        "access_token": access_token,
        "details": true_user
    }

    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def teacher_check(request):
    response = Response()

    try:
        true_user = user.object.get(user_uuid=request.POST.get("user_uuid"))

        current_date = datetime.utcfromtimestamp(
            datetime.datetime.utcnow()).strftime('%d/%m/%Y')

        queryset = attendance.objects.filter(
            attendance_user=true_user, attendance_date=current_date)

        response.status = status.HTTP_409_CONFLICT
        response.data = {
            "message": "Checked in",
            "details": {}
        }
    except ObjectDoesNotExist:
        # true_schedule = schedule.object.get(schedule_class.classes_name=request.POST.get("class_name"),user_uuid=request.POST.get("user_uuid"))

        serializer = AttendanceSerializer()

        serializer = AttendanceSerializer(data={
            "image_gallery_user_uuid": request.POST.get("user_uuid"),
            "image_gallery_name": name,
            "image_gallery_uuid": image_uuid,
            "image_gallery_path": path,
            "image_gallery_size": size,
            "image_gallery_created_at": datetime.datetime.utcnow().timestamp(),
            "image_gallery_updated_at": datetime.datetime.utcnow().timestamp()
        })
        # print(serializer)
        if serializer.is_valid():
            serializer.save()
        else:
            response.status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response.data = {
                "message": "Server error",
                "details": {}
            }

        response.status = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.data = {
            "message": "Server error",
            "details": {}
        }

    return response


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
