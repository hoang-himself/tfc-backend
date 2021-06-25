from uuid import uuid4
from django.conf import settings
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
