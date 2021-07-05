from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app_auth.utils import gen_ref_token, gen_acc_token
from master_db.serializers import CustomUserSerializer

import jwt


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login(request) -> Response:
    CustomUser = get_user_model()
    valid = True
    errors = {}

    email = request.POST.get('email')
    password = request.POST.get('password')

    if not email:
        errors['email'] = 'This field is required.'
        valid = False

    if not password:
        errors['password'] = 'This field is required.'
        valid = False

    if (valid == False):
        return Response(
            data={
                'detail': errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = get_object_or_404(CustomUser, email=email)

    tmp_user = CustomUserSerializer(user).data
    if not check_password(password, tmp_user.get('password')):
        return Response(
            data={
                'detail': 'User not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    refresh_token = gen_ref_token(user)
    access_token = gen_acc_token(user)

    response = Response()
    response.set_cookie(key='accesstoken', value=access_token, httponly=True)
    response.status_code = status.HTTP_200_OK
    response.data = {
        'token': {
            'refresh': refresh_token,
        }
    }
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def check(request):
    access_token = request.COOKIES.get('accesstoken')

    if not access_token:
        return Response(
            data={
                'message': 'User not logged in.'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
        if payload.get('typ') != 'access':
            return Response(
                data={
                    'message': 'Invalid access token.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    except jwt.ExpiredSignatureError:
        return Response(
            data={
                'message': 'Session expired.'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    return Response(
        data={
            'role': payload.get('role'),
            'perms': payload.get('perms')
        },
        status=status.HTTP_200_OK
    )


@api_view(['DELETE'])
@permission_classes([AllowAny])
def logout(request) -> Response:
    response = Response()

    # TODO Add token to blacklist

    access_token = request.COOKIES.get('accesstoken', None)
    csrf_token = request.COOKIES.get('csrftoken', None)

    if not (access_token):
        response.status_code = status.HTTP_204_NO_CONTENT
        response.data = {
            'message': 'User is already logged out.'
        }
        return response
    if access_token:
        response.delete_cookie('accesstoken')
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
    CustomUser = get_user_model()
    refresh_token = request.COOKIES.get('refresh')

    if not refresh_token:
        return Response(
            data={
                "refresh": "This field is required."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        if payload.get('typ') != 'refresh':
            return Response(
                data={
                    'message': 'Invalid refresh token.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    except jwt.ExpiredSignatureError:
        return Response(
            data={
                'message': 'Session expired.'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    user = get_object_or_404(CustomUser, uuid=payload.get('user_id'))

    if not user.is_active:
        return Response(
            data={
                'message': 'User inactive.'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    access_token = gen_acc_token(user)

    response = Response()
    response.set_cookie(key='accesstoken', value=access_token, httponly=True)
    response.status_code = status.HTTP_200_OK
    response.data = {}
    return response
