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

    sign = settings.SECRET_KEY + user['password'][-50:]
    token = jwt.encode(payload, sign, algorithm='HS256')
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

    sign = settings.SECRET_KEY + user['password'][-50:]
    token = jwt.encode(payload, sign, algorithm='HS256')
    return token


def decode_token(refresh_token):
    result = -2
    claims = None
    if (refresh_token == None):
        return (result, None)
    try:
        claims = jwt.decode(
            refresh_token, options={"verify_signature": False}, issuer='TFC', algorithms=['HS256'])
        result = 0
    except jwt.DecodeError:
        result = -1
    except jwt.InvalidSignatureError:
        result = 1
    except jwt.ExpiredSignatureError:
        result = 2
    except jwt.InvalidAudienceError:
        result = 3
    except jwt.InvalidIssuerError:
        result = 4
    except jwt.InvalidIssuedAtError:
        result = 5
    except jwt.ImmatureSignatureError:
        result = 6
    except jwt.exceptions.InvalidKeyError:
        result = 7
    except jwt.InvalidAlgorithmError:
        result = 8
    return (result, claims)
