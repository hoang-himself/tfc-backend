from django.contrib.auth.hashers import check_password

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from master_db.models import MyUser
from master_db.serializers import MyUserSerializer
from master_api.utils import gen_ref_token, gen_acc_token, decode_token


@api_view(['POST'])
@permission_classes([AllowAny])
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
def check(request):
    response = Response()
    token = request.POST.get('token')

    if (token is None or token == ''):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {
            "token": [
                "This field is required"
            ]
        }
        return response

    payload = decode_token(token)
    flag, claims = payload

    if (flag != 0):
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            "token": [
                "Token invalid or expired"
            ]
        }
        return response

    response.status_code = status.HTTP_200_OK
    response.data = {
        "role": claims['role'],
        "perms": claims['perms']
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
def refresh(request):
    response = Response()
    token = request.POST.get('refresh')

    if (token is None or token == ''):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {
            "refresh": [
                "This field is required"
            ]
        }
        return response

    payload = decode_token(token)
    flag, claims = payload

    if (flag != 0 or claims['typ'] != 'refresh'):
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            "refresh": [
                "Refresh token invalid or expired"
            ]
        }
        return response

    user = MyUser.objects.filter(uuid=claims['user_id']).first()
    if (user is None):
        response.data = {
            "user": [
                "Not found"
            ]
        }
        return response

    access_token = gen_acc_token(user)

    response.status_code = status.HTTP_200_OK
    response.data = {
        "token": {
            "access": access_token
        }
    }
    return response
