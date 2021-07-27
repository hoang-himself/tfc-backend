from annoying.functions import get_object_or_None

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework.exceptions import APIException

import jwt


CustomUser = get_user_model()


class BadAccessToken(APIException):
    status_code = 400
    default_detail = 'Invalid access token'
    default_code = 'bad_access_token'


class BadRefreshToken(APIException):
    status_code = 400
    default_detail = 'Invalid refresh token'
    default_code = 'bad_refresh_token'


class NotLoggedIn(APIException):
    status_code = 401
    default_detail = 'User not logged in.'
    default_code = 'not_logged_in'


class SessionExpired(APIException):
    status_code = 401
    default_detail = 'Session expired.'
    default_code = 'session_expired'


class UserNotFound(APIException):
    status_code = 404
    default_detail = 'User not found.'
    default_code = 'user_not_found'


class UserInactive(APIException):
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
