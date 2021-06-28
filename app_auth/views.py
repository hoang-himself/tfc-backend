from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from master_db.models import MyUser
from master_db.serializers import MyUserSerializer
from app_auth.utils import gen_ref_token, gen_acc_token

import jwt


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login(request) -> Response:
    response = Response()
    response.status_code = status.HTTP_400_BAD_REQUEST
    valid = True
    errors = {}

    username = request.POST.get('username')
    password = request.POST.get('password')

    if not username:
        errors['username'] = 'This field is required.'
        valid = False

    user = get_object_or_404(MyUser, username=username)

    if not password:
        errors['password'] = 'This field is required.'
        valid = False

    if (valid == False):
        response.data = {
            'detail': errors
        }
        return response

    tmp_user = MyUserSerializer(user).data
    if not check_password(password, tmp_user['password']):
        response.status_code = status.HTTP_404_NOT_FOUND
        response.data = {
            'detail': 'Not found.'
        }
        return response

    refresh_token = gen_ref_token(user)
    access_token = gen_acc_token(user)

    response.set_cookie(key='accesstoken', value=access_token, httponly=True)
    response.set_cookie(key='refreshtoken',
                        value=refresh_token, httponly=True)
    response.status_code = status.HTTP_200_OK
    response.data = {
        'token': {
            'refresh': refresh_token,
            'access': access_token
        }
    }
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def check(request):
    response = Response()
    access_token = request.COOKIES.get('accesstoken')

    if not access_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {
            'message': 'User not logged in.'
        }
        return response
    try:
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {
            'message': 'Session expired.'
        }
        return response

    if payload['typ'] != 'access':
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            'message': 'Invalid access token.'
        }
        return response

    response.status_code = status.HTTP_200_OK
    response.data = {
        'role': payload['role'],
        'perms': payload['perms']
    }
    return response


@api_view(['DELETE'])
@permission_classes([AllowAny])
def logout(request) -> Response:
    response = Response()

    # TODO Add token to blacklist

    access_token = request.COOKIES.get('accesstoken', None)
    refresh_token = request.COOKIES.get('refreshtoken', None)
    csrf_token = request.COOKIES.get('csrftoken', None)

    if not (access_token and refresh_token):
        response.status_code = status.HTTP_200_OK
        response.data = {
            'message': 'User is already logged out.'
        }
        return response
    if access_token:
        response.delete_cookie('accesstoken')
    if refresh_token:
        response.delete_cookie('refreshtoken')
    if csrf_token:
        response.delete_cookie('csrftoken')

    response.status_code = status.HTTP_204_NO_CONTENT
    response.data = {
        'message': 'Logged out successfully.'
    }
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def refresh(request):
    response = Response()
    refresh_token = request.COOKIES.get('refreshtoken')

    if not refresh_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {
            'message': 'User not logged in.'
        }
        return response

    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {
            'message': 'Session expired.'
        }
        return response

    if payload['typ'] != 'refresh':
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            'message': 'Invalid refresh token.'
        }
        return response

    user = get_object_or_404(MyUser, uuid=payload['user_id'])

    if not user.is_active:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {
            'message': 'User inactive.'
        }
        return response

    access_token = gen_acc_token(user)

    response.set_cookie(key='accesstoken', value=access_token, httponly=True)
    response.status_code = status.HTTP_200_OK
    response.data = {
        'token': {
            'access': access_token
        }
    }
    return response
