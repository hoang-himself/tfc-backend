from django.conf import settings

import datetime
import jwt


def generate_access_token(user, role=None, perms=None, alg='HS256'):
    access_token_payload = {
        'iss': '',
        'sub': user.get('uuid'),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
        'iat': datetime.datetime.utcnow(),
        'jti': '',
        'role': role,
        'perms': perms,
    }

    access_token = jwt.encode(access_token_payload,
                              settings.JWT_ACCESS_KEY, algorithm=alg).decode('utf-8')
    return access_token


def generate_refresh_token(user, alg='HS256'):
    refresh_token_payload = {
        'iss': '',
        'sub': user.get('uuid'),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=14),
        'iat': datetime.datetime.utcnow(),
        'jti': ''
    }

    refresh_token = jwt.encode(refresh_token_payload,
                               settings.JWT_REFRESH_KEY, algorithm=alg).decode('utf-8')
    return refresh_token


def decode_refresh_token(refresh_token, algs=['HS256']):
    result = -2
    claims = None
    if (refresh_token == None):
        return (result, None)
    try:
        claims = jwt.decode(
            refresh_token, settings.JWT_REFRESH_KEY, algorithms=algs)
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
