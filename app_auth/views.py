from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from master_db.models import MyUser
from master_db.serializers import UserSerializer
from master_api.jwt import RefreshToken


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request) -> Response:
    response = Response()
    response.status_code = status.HTTP_400_BAD_REQUEST
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

    user = MyUser.objects.filter(username=username).first()
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

    refresh_token = RefreshToken(user)
    access_token = refresh_token.access_token

    response.status_code = status.HTTP_202_ACCEPTED
    response.data = {
        "result": "ok",
        "token": {
            "access": str(access_token),
            "refresh": str(refresh_token)
        }
    }
    return response


@api_view(['GET'])
@permission_classes([AllowAny])
def check(request):
    pass


@api_view(['DELETE'])
@permission_classes([AllowAny])
def logout(request) -> Response:
    """
    response = Response()
    response.status_code = status.HTTP_400_BAD_REQUEST

    refresh_token = request.POST.get('refresh')

    if (refresh_token is None or refresh_token == ''):
        response.data = {
            "refresh": [
                'This field is required'
            ]
        }
        return response

    try:
        refresh = RefreshToken(refresh_token)
    except TokenError:
        response.data = {
            "detail": "Token has wrong type",
            "code": "token_not_valid"
        }
        return response

    refresh.blacklist()

    response.status_code = status.HTTP_204_NO_CONTENT
    response.data = {
        "result": "ok"
    }

    return response
    """
    pass


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh(request):
    pass
