from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from master_db.models import MyUser
from master_db.serializers import MyUserSerializer
from master_api.utils import gen_ref_token, gen_acc_token

import jwt


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login(request) -> Response:
    response = Response()
    response.status_code = status.HTTP_400_BAD_REQUEST
    valid = True
    errors = []

    username = request.POST.get('username')
    password = request.POST.get('password')

    if (username is None or username == ''):
        errors.append(
            {
                "username": [
                    "This field is required"
                ]
            }
        )
        valid = False
    if (password is None or password == ''):
        errors.append(
            {
                "password": [
                    "This field is required"
                ]
            }
        )
        valid = False
    if (valid == False):
        response.data = {
            errors
        }
        return response

    user = MyUser.objects.filter(username=username).first()
    if (user is None):
        response.data = {
            "username": [
                "Not found"
            ]
        }
        return response

    tmp_user = MyUserSerializer(user).data
    if not check_password(password, tmp_user.get("password")):
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            "password": [
                "No matching username and password"
            ]
        }
        return response

    refresh_token = gen_ref_token(user)
    access_token = gen_acc_token(user)

    response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
    response.status_code = status.HTTP_202_ACCEPTED
    response.data = {
        "token": {
            "access": access_token
        }
    }
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def check(request):
    response = Response()
    refresh_token = request.COOKIES.get('refreshtoken')

    if refresh_token is None:
        raise exceptions.AuthenticationFailed(
            'Authentication credentials were not provided')
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed(
            'Refresh token expired')

    user = MyUser.objects.filter(uuid=payload['user_id']).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')

    if not user.is_active:
        raise exceptions.AuthenticationFailed('user is inactive')

    response.status_code = status.HTTP_200_OK
    response.data = {
        "role": payload['role'],
        "perms": payload['perms']
    }
    return response


@api_view(['DELETE'])
@permission_classes([AllowAny])
def logout(request) -> Response:
    """
    response = Response()
    response.status_code = status.HTTP_400_BAD_REQUEST
    valid = 1
    errors = []

    refresh_token = request.POST.get('refresh')
    access_token = request.POST.get('access')

    if (refresh_token is None or refresh_token == ''):
        errors.append(
            {
                "refresh": [
                    "This field is required"
                ]
            }
        )
        valid -= 1
    if (access_token is None or access_token == ''):
        errors.append(
            {
                "access": [
                    "This field is required"
                ]
            }
        )
        valid -= 1
    if (valid < 1):
        response.data = {
            errors
        }
        return response

    response.status_code = status.HTTP_204_NO_CONTENT
    response.data = {
        "result": "ok"
    }
    return response
    """
    pass


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def refresh(request):
    response = Response()
    refresh_token = request.COOKIES.get('refreshtoken')

    if refresh_token is None:
        raise exceptions.AuthenticationFailed(
            'Authentication credentials were not provided')
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed(
            'Refresh token expired')

    user = MyUser.objects.filter(uuid=payload['user_id']).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')

    if not user.is_active:
        raise exceptions.AuthenticationFailed('user is inactive')

    access_token = gen_acc_token(user)

    response.status_code = status.HTTP_200_OK
    response.data = {
        "token": {
            "access": access_token
        }
    }
    return response
