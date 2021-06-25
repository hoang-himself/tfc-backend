from django.conf import settings
from rest_framework import status
from master_db.serializers import MyUserSerializer, RoleSerializer

import datetime
import jwt


def gen_ref_token(user):
    payload = {}

    role = RoleSerializer(user.role).data
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

    role = RoleSerializer(user.role).data
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

    authorization_header = request.headers.get('Authorization')

    if not authorization_header:
        return None
    try:
        # header = 'Token xxxxxxxxxxxxxxxxxxxxxxxx'
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return status.HTTP_401_UNAUTHORIZED
    except IndexError:
        return status.HTTP_400_BAD_REQUEST

    if (access_token is None or access_token == ''):
        return status.HTTP_400_BAD_REQUEST

    try:
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return status.HTTP_400_BAD_REQUEST

    claimed_perms = payload['perms']
    for perm in perms:
        if perm in claimed_perms:
            return status.HTTP_200_OK
    return status.HTTP_401_UNAUTHORIZED
