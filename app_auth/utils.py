from annoying.functions import get_object_or_None

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import exceptions

import jwt


CustomUser = get_user_model()
JWT_KEY = settings.JWT_KEY


def request_to_jwt(request):
    authorization_header = request.headers.get('Authorization')

    try:
        access_token = authorization_header.split(' ')[1]
        jwt.decode(access_token, JWT_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed('Access token expired')
    except IndexError:
        raise exceptions.AuthenticationFailed('Token prefix missing')


class BadAccessToken(exceptions.APIException):
    status_code = 400
    default_detail = 'Invalid access token'
    default_code = 'bad_access_token'


class BadRefreshToken(exceptions.APIException):
    status_code = 400
    default_detail = 'Invalid refresh token'
    default_code = 'bad_refresh_token'


class NotLoggedIn(exceptions.APIException):
    status_code = 401
    default_detail = 'User not logged in.'
    default_code = 'not_logged_in'


class SessionExpired(exceptions.APIException):
    status_code = 401
    default_detail = 'Session expired.'
    default_code = 'session_expired'


class UserNotFound(exceptions.APIException):
    status_code = 404
    default_detail = 'User not found.'
    default_code = 'user_not_found'


class UserInactive(exceptions.APIException):
    status_code = 404
    default_detail = 'User inactive.'
    default_code = 'user_inactive'


def request_to_userobj(request):
    access_token = request.COOKIES.get('accesstoken')

    if not (access_token):
        raise NotLoggedIn()

    try:
        payload = jwt.decode(
            access_token, settings.JWT_KEY, algorithms=['HS256'])
        if payload.get('typ') != 'access':
            raise BadAccessToken()
    except jwt.ExpiredSignatureError:
        raise SessionExpired()

    if ((user := get_object_or_None(CustomUser, uuid=payload.get('uuid'))) is None):
        raise UserNotFound()

    if not user.is_active:
        raise UserInactive()

    return user
