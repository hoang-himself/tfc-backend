from annoying.functions import get_object_or_None

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import update_last_login

from rest_framework import status
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import (csrf_protect, ensure_csrf_cookie)

from rest_framework_simplejwt.tokens import RefreshToken
from master_db.serializers import EnhancedModelSerializer

import jwt

CustomUser = get_user_model()
JWT_KEY = settings.JWT_KEY


class CustomUserSerializer(EnhancedModelSerializer):

    class Meta:
        model = CustomUser
        exclude = ('id',)


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login(request) -> Response:
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

    if ((user := get_object_or_None(CustomUser, email=email)) is None):
        return Response(
            data={
                'detail': 'User not found.'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    ser_user = CustomUserSerializer(user).data
    if not check_password(password, ser_user.get('password')):
        return Response(
            data={
                'detail': 'User not found.'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    refresh_token = RefreshToken.for_user(user)
    access_token = refresh_token.access_token
    update_last_login(None, user)

    response = Response()
    response.set_cookie(
        key='accesstoken',
        value=str(access_token),
        httponly=True
    )
    response.status_code = status.HTTP_200_OK
    response.data = {
        'token': {
            'refresh': str(refresh_token),
        }
    }
    return response


@api_view(['DELETE'])
@permission_classes([AllowAny])
def logout(request) -> Response:
    refresh_token = request.POST.get('refresh')
    access_token = request.COOKIES.get('accesstoken')

    if not (access_token):
        return Response(
            data={
                'detail': 'User not logged in.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if not (refresh_token):
        return Response(
            data={
                'refresh': 'This field is required.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    response = Response()
    response.delete_cookie('accesstoken')
    # RefreshToken(refresh_token).blacklist() # TODO
    response.status_code = status.HTTP_200_OK
    response.data = {
        'detail': 'Ok'
    }
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def refresh(request):
    refresh_token = request.POST.get('refresh')

    if not (refresh_token):
        return Response(
            data={
                'refresh': 'This field is required.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        payload = jwt.decode(
            refresh_token, JWT_KEY, algorithms=['HS256'])
        if payload.get('typ') != 'refresh':
            return Response(
                data={
                    'detail': 'Invalid refresh token.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    except jwt.ExpiredSignatureError:
        return Response(
            data={
                'detail': 'Session expired.'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    if ((user := get_object_or_None(CustomUser, uuid=payload.get('uuid'))) is None):
        return Response(
            data={
                'detail': 'User not found.'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    if not user.is_active:
        return Response(
            data={
                'detail': 'User inactive.'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    access_token = RefreshToken.for_user(user).access_token

    response = Response()
    response.set_cookie(key='accesstoken', value=str(
        access_token), httponly=True)
    response.status_code = status.HTTP_200_OK
    response.data = {
        'detail': 'Ok'
    }
    return response


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
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

        if ((user := get_object_or_None(CustomUser, email=email)) is None):
            return Response(
                data={
                    'detail': 'User not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        ser_user = CustomUserSerializer(user).data
        if not check_password(password, ser_user.get('password')):
            return Response(
                data={
                    'detail': 'User not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        update_last_login(None, user)

        response = Response()
        response.set_cookie(
            key='accesstoken',
            value=str(access_token),
            httponly=True
        )
        response.status_code = status.HTTP_200_OK
        response.data = {
            'token': {
                'refresh': str(refresh_token),
            }
        }
        return response


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request):
        refresh_token = request.POST.get('refresh')
        access_token = request.COOKIES.get('accesstoken')

        if not (access_token):
            return Response(
                data={
                    'detail': 'User not logged in.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if not (refresh_token):
            return Response(
                data={
                    'refresh': 'This field is required.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        response = Response()
        response.delete_cookie('accesstoken')
        # RefreshToken(refresh_token).blacklist() # TODO
        response.status_code = status.HTTP_200_OK
        response.data = {
            'detail': 'Ok'
        }
        return response


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.POST.get('refresh')

        if not (refresh_token):
            return Response(
                data={
                    'refresh': 'This field is required.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payload = jwt.decode(
                refresh_token, JWT_KEY, algorithms=['HS256'])
            if payload.get('typ') != 'refresh':
                return Response(
                    data={
                        'detail': 'Invalid refresh token.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except jwt.ExpiredSignatureError:
            return Response(
                data={
                    'detail': 'Session expired.'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if ((user := get_object_or_None(CustomUser, uuid=payload.get('uuid'))) is None):
            return Response(
                data={
                    'detail': 'User not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if not user.is_active:
            return Response(
                data={
                    'detail': 'User inactive.'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        access_token = RefreshToken.for_user(user).access_token

        response = Response()
        response.set_cookie(key='accesstoken', value=str(
            access_token), httponly=True)
        response.status_code = status.HTTP_200_OK
        response.data = {
            'detail': 'Ok'
        }
        return response
