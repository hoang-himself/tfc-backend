from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
# from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect

from master_db.serializers import UserSerializer
from .utils import (
    generate_access_token,
    generate_refresh_token,
    validate_refresh_token,
)


@api_view(['POST'])
@permission_classes([AllowAny])
# @ensure_csrf_cookie
def login(request) -> Response:
    response = Response()
    response.status_code = status.HTTP_400_BAD_REQUEST
    User = get_user_model()
    valid = 1
    errors = []

    username = request.POST.get('username')
    password = request.POST.get('password')

    if (username is None or username == ''):
        errors.append(
            {
                "username": "required"
            }
        )
        valid -= 1
    if (password is None or password == ''):
        errors.append(
            {
                "password": "required"
            }
        )
        valid -= 1
    if (valid < 1):
        response.data = {
            "result": "error",
            "errors": errors
        }
        return response

    user = User.objects.filter(username=username).first()
    if (user is None):
        response.data = {
            "result": "error",
            "errors": [
                {
                    "username": "not_found"
                }
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
                    "password": "no_match"
                }
            ]
        }
        return response

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)

    response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
    response.status_code = status.HTTP_202_ACCEPTED
    response.data = {
        "result": "ok",
        "token": {
            "access": access_token
        }
    }
    return response


def refresh_token_response(refresh_token):
    response = Response()
    User = get_user_model()
    response.status_code = status.HTTP_403_FORBIDDEN

    (result, payload) = validate_refresh_token(refresh_token)

    if (result != 0):
        # You want switch-case? Install python 3.10
        if (result == -2):
            response.status_code = status.HTTP_401_UNAUTHORIZED
            response.data = {
                "result": "error",
                "errors": [
                    "not logged in"
                ]
            }
        elif (result == 2):
            response.data = {
                "result": "error",
                "errors": [
                    "expired",
                    "refreshtoken"
                ]
            }
        else:
            response.data = {
                "result": "error",
                "errors": [
                    "invalid",
                    "refreshtoken"
                ]
            }
        return (None, response)

    user = User.objects.filter(username=payload.get('sub')).first()
    if (user is None):
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            "result": "error",
            "errors": [
                {
                    "user": "not found"
                },
            ]
        }
        return (user, response)
    if not (user.is_active):
        response.status_code = status.HTTP_403_FORBIDDEN
        response.data = {
            "result": "error",
            "errors": [
                {
                    "user": "inactive"
                },
            ]
        }
        return (None, response)
    return (user, response)


@api_view(['GET'])
@permission_classes([AllowAny])
def check(request) -> Response:
    response = Response()
    response.status_code = status.HTTP_403_FORBIDDEN

    refresh_token = request.COOKIES.get('refreshtoken')
    user, response = refresh_token_response(refresh_token)
    if (user is None):
        return response

    roles = [
        # TODO
    ]
    permissions = [
        # TODO
    ]

    response.status_code = status.HTTP_200_OK
    response.data = {
        "result": "ok",
        "isAuthenticated": True,
        "roles": roles,
        "permissions": permissions,
    }
    return response


@api_view(['DELETE'])
@permission_classes([AllowAny])
def logout(request) -> Response:
    pass


@api_view(['POST'])
@permission_classes([AllowAny])
# @csrf_protect
def refresh(request) -> Response:
    response = Response()

    refresh_token = request.COOKIES.get('refreshtoken')
    token_data = refresh_token_response(refresh_token)
    user, response = token_data
    if (user is None):
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
