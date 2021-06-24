from django.utils.translation import gettext_lazy as _
from uuid import uuid4
from django.conf import settings
import datetime
import jwt


def RefreshToken(user):
    payload = {}

    payload['typ'] = 'refresh'
    payload['iss'] = 'TFC'
    payload['sub'] = user.get('uuid')
    payload['exp'] = datetime.datetime.utcnow() + \
        datetime.timedelta(days=1)
    payload['iat'] = datetime.datetime.utcnow()
    payload['nbf'] = datetime.datetime.utcnow()
    payload['jti'] = uuid4().hex

    token = jwt.encode(payload,
                       settings.JWT_REF_KEY, algorithm='HS256').decode('utf-8')
    return token


def AccessToken(user):
    payload = {}

    payload['typ'] = 'access'
    payload['iss'] = 'TFC'
    payload['sub'] = user.get('uuid')
    payload['exp'] = datetime.datetime.utcnow() + \
        datetime.timedelta(minutes=15)
    payload['iat'] = datetime.datetime.utcnow()
    payload['nbf'] = datetime.datetime.utcnow()
    payload['jti'] = uuid4().hex

    token = jwt.encode(payload,
                       settings.JWT_ACC_KEY, algorithm='HS256').decode('utf-8')
    return token
