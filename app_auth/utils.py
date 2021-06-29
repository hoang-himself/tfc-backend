from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from master_db.serializers import MyUserSerializer, MyGroupSerializer

import datetime
import jwt


def gen_ref_token(user):
    payload = {}

    role = MyGroupSerializer(user.role).data
    perms = []
    not_role = ['id', 'name', 'created_at', 'updated_at']
    for key in role:
        if key in not_role:
            continue
        elif role[key] == True:
            perms.append(key)

    user = MyUserSerializer(user).data

    payload['typ'] = 'refresh'
    payload['iss'] = 'TFC'
    payload['exp'] = datetime.datetime.utcnow() + \
        datetime.timedelta(days=1)
    payload['iat'] = datetime.datetime.utcnow()
    payload['nbf'] = datetime.datetime.utcnow()
    payload['jti'] = ''
    payload['role'] = role['name']
    payload['perms'] = perms
    payload['user_id'] = user['uuid']

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


def gen_acc_token(user):
    payload = {}

    role = MyGroupSerializer(user.role).data
    perms = []
    not_role = ['id', 'name', 'created_at', 'updated_at']
    for key in role:
        if key in not_role:
            continue
        elif role[key] == True:
            perms.append(key)

    user = MyUserSerializer(user).data

    payload['typ'] = 'access'
    payload['iss'] = 'TFC'
    payload['exp'] = datetime.datetime.utcnow() + \
        datetime.timedelta(minutes=15)
    payload['iat'] = datetime.datetime.utcnow()
    payload['nbf'] = datetime.datetime.utcnow()
    payload['jti'] = ''
    payload['role'] = role['name']
    payload['perms'] = perms
    payload['user_id'] = user['uuid']

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token


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
