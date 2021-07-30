from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import exceptions

import jwt


CustomUser = get_user_model()
JWT_KEY = settings.JWT_KEY


def request_header_to_jwt(request):
    # 'Authorization': 'JWT <token>'
    authorization_header = request.headers.get('Authorization')

    try:
        token = authorization_header.split(' ')[1]
    except IndexError:
        raise exceptions.ParseError({'HTTP_AUTHORIZATION': 'Token prefix missing'})

    return token


def request_header_to_userobj(request):
    # 'Authorization': 'JWT <token>'
    token = request_header_to_jwt(request)

    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed(
            {'token': 'Access token expired'}
        )

    return payload
