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
    errors = {}

    username = request.POST.get('username')
    password = request.POST.get('password')

    if (username is None or username == ''):
        errors["username"] = "This field is required"
        valid = False
    if (password is None or password == ''):
        errors["password"] = "This field is required"
        valid = False
    if (valid == False):
        response.data = errors
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

    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.status_code = status.HTTP_202_ACCEPTED
    response.data = {
        "token": {
            "refresh": refresh_token,
            "access": access_token
        }
    }
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def check(request):
    response = Response()
    access_token = request.COOKIES.get('access_token')

    if access_token is None:
        raise exceptions.AuthenticationFailed(
            'Authentication credentials were not provided')
    try:
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed(
            'Refresh token expired')

    response.status_code = status.HTTP_200_OK
    response.data = {
        "role": payload['role'],
        "perms": payload['perms']
    }
    return response


@api_view(['DELETE'])
@permission_classes([AllowAny])
def logout(request) -> Response:
    response = Response()

    # TODO
    access_token = request.COOKIES.get('access_token', None)
    if access_token:
        response.delete_cookie('access_token')
        response.status_code = status.HTTP_204_NO_CONTENT
        response.data = {
            'message': 'Logged out successfully.'
        }
        return response

    response.status_code = status.HTTP_200_OK
    response.data = {
        'message': 'User is already logged out.'
    }
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def refresh(request):
    response = Response()
    refresh_token = request.POST.get('refresh')

    if not refresh_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {
            'message': 'User not logged in'
        }
        return response

    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {
            'message': 'Session expired'
        }
        return response

    user = MyUser.objects.filter(uuid=payload['user_id']).first()
    if user is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            'message': 'User not found'
        }
        return response

    if not user.is_active:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {
            'message': 'User inactive'
        }
        return response

    access_token = gen_acc_token(user)

    response.set_cookie(key='access_token', value=access_token, httponly=True)
    response.status_code = status.HTTP_200_OK
    response.data = {
        "token": {
            "access": access_token
        }
    }
    return response
