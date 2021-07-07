from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

import jwt


def has_perm(request, perms):
    response = Response()
    access_token = request.COOKIES.get('accesstoken')

    if not access_token:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {
            'message': 'User not logged in'
        }
        return response

    try:
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        response.data = {
            'message': 'Session expired'
        }
        return response

    if payload['typ'] != 'access':
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {
            'message': 'Invalid access token'
        }
        return response

    claimed_perms = payload['perms']
    for perm in perms:
        if perm in claimed_perms:
            response.status_code = status.HTTP_200_OK
            response.data = {
                'message': 'Authorized'
            }
            return response

    response.status_code = status.HTTP_401_UNAUTHORIZED
    response.data = {
        'message': 'Unauthorized'
    }
    return response
