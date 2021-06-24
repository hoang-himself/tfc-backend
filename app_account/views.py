from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from master_db.models import Role
from master_db.serializers import UserSerializer

import re
import datetime
import uuid as uuid_gen
import json
import jwt
import base64
from cryptography.fernet import Fernet

# Create your views here.


def email_validate(email) -> bool:
    """
        Validate email address format
    """
    # Check nullity
    if email is None:
        return False

    # Validating email address
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if re.search(regex, email):
        return True
    else:
        return False


def email_response(email) -> Response:
    """
        Return response when checking signed up email address in db
    """
    # Validating email address
    if not email_validate(email):
        return Response(
            data={
                "details": "Error",
                "message": "Invalid email address"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check for existence
    if get_user_model().objects.filter(email=email).exists():
        return Response(
            data={
                "details": "Error",
                "message": "Email has already existed"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        return Response(
            data={
                "details": "Ok",
                "message": "Email is suitable for creating user"
            },
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def email_check(request) -> Response:
    """
        API for checking email address for creating user
    """
    email = request.POST.get('email')
    return Response(email)


def mobile_validate(mobile) -> bool:
    """
        Validate phone number format
    """
    # Check nullity
    if mobile is None:
        return False

    # Validating mobile phone number
    regex = '^(0?)(3[2-9]|5[6|8|9]|7[0|6-9]|8[0-6|8|9]|9[0-4|6-9])[0-9]{7}$'
    if re.search(regex, mobile):
        return True
    else:
        return False


def mobile_response(mobile) -> Response:
    """
        Return response when checking signed up mobile phone number in db
    """
    # Validating mobile address
    if not mobile_validate(mobile):
        return Response(
            data={
                "details": "Error",
                "message": "Invalid mobile phone number "
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check for existence
    if get_user_model().objects.filter(mobile=mobile).exists():
        return Response(
            data={
                "details": "Error",
                "message": "Mobile phone number has already existed"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        return Response(
            data={
                "details": "Ok",
                "message": "Mobile phone number is suitable for creating user"
            },
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def mobile_check(request) -> Response:
    """
        API for checking phone number for creating user
    """
    mobile = request.POST.get('mobile')
    return mobile_response(mobile)


def username_response(uid) -> Response:
    """
        Return response when checking signed up UID in db
    """
    # Check for existence
    if get_user_model().objects.filter(uid=uid).exists():
        return Response(
            data={
                "details": "Error",
                "message": "Username has already existed"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        return Response(
            data={
                "details": "Ok",
                "message": "Username is suitable for creating user"
            },
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def username_check(request) -> Response:
    """
        API for checking username for creating user
    """
    uid = request.POST.get('uid')
    return username_response(uid)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request) -> Response:
    """
        Requires every param: first_name, last_name, address, male, avatar, birth_date, role_id, email, mobile, username, password.

        The role_id param takes in int type and represents the id of the role in database.
    """

    # Insignificant factors:
    # - These factors are freely defined and do not affect
    # its corresponding account if input incorrectly.

    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    address = request.POST.get('address')
    male = request.POST.get('male')
    avatar = request.POST.get('avatar')
    birth_date = request.POST.get('birth_date')

    # Significant factors:
    # - These are the opposite of the insignificant factors,
    # they greately affect the user account.
    # There must be a strict rule for these to obey.

    # Verify email address
    email = request.POST.get('email')
    mobile = request.POST.get('mobile')
    username = request.POST.get('username')
    password = request.POST.get('password')

    # Verify email address
    check = email_response(email)
    if check.status_code == status.HTTP_400_BAD_REQUEST:
        return Response(
            data={
                "details": "Error",
                "message": check.data["message"],
            }
        )

    # Verify mobile phone number
    check = mobile_response(mobile)
    if check.status_code == status.HTTP_400_BAD_REQUEST:
        return Response(
            data={
                "details": "Error",
                "message": check.data["message"],
            }
        )

    # Verify username
    check = username_response(username)
    if check.status_code == status.HTTP_400_BAD_REQUEST:
        return Response(
            data={
                "details": "Error",
                "message": check.data["message"]
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # TODO: Handling password

    # DB generated factor:
    # - These are generated automatically and seperated from
    # user input

    created_at = datetime.datetime.now().timestamp()
    updated_at = created_at
    uuid = uuid_gen.uuid4()
    role_id = request.POST.get('role_id')

    # Check UUID uniqueness
    while get_user_model().objects.filter(uuid=uuid).exists():  # ! Ensure uniqueness, may be a bad algorithm
        uuid = uuid_gen.uuid4()

    # Get role from role_id
    role = Role.objects.filter(id=role_id)
    if role.exists():
        role = role.first()
    else:
        return Response(
            data={
                'details': 'Error',
                'message': 'Role does not exist'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    #
    newUser = get_user_model()(
        uuid=uuid,
        uid=username,
        first_name=first_name,
        last_name=last_name,
        birth_date=birth_date,
        email=email,
        mobile=mobile,
        male=male,
        password=password,
        address=address,
        role_id=role,
        avatar=avatar,
        created_at=created_at,
        updated_at=updated_at,
    )

    dictionary = UserSerializer(newUser, many=False)
    serializer = UserSerializer(data=dictionary.data)

    # If required fields are empty function returns Django implemented exception
    if serializer.is_valid(raise_exception=True):
        # TODO: Save the user
        # serializer.save()
        return Response(
            data={
                "details": "Ok",
                "message": "Successfully created",
                "user": serializer.data,  # ! For testing purposes only - should be removed
            },
            status=status.HTTP_201_CREATED
        )

    return Response(
        data={
            "details": "Error",
            "message": "Don't know how you got here but here we are",
        },
        status=status.HTTP_501_NOT_IMPLEMENTED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def send_activation(request) -> Response:
    """
        Take in email and return a token for activating account
    """
    email = request.GET.get('email')

    # Check for existence
    if not get_user_model().objects.filter(email=email).exists():
        return Response(
            data={
                "details": "Error",
                'message': 'Email not found',
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    data = {
        "aud": email,
        "exp": datetime.datetime.timestamp(datetime.datetime.utcnow() + datetime.timedelta(days=1)),
        "iat": datetime.datetime.timestamp(datetime.datetime.utcnow()),
    }

    # TODO: Encrypt data
    data = json.dumps(data).encode('utf-8')
    # ! Hardcoding: A byte-like string with length = 32
    key = base64.urlsafe_b64encode(b"PBKDFJHMACGEJHYRSNJSWASHYESGYWSA")
    cipher_suite = Fernet(key)
    data = cipher_suite.encrypt(data)

    return Response(
        data={
            'details': 'Ok',
            'code': data,
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def activate(request):
    """
        Take in a token, activate the account decrypted from that token and return state of activation
    """
    code = request.GET.get('code')

    # TODO: Decrypt data
    # ! Hardcoding: A byte-like string with length = 32
    key = base64.urlsafe_b64encode(b"PBKDFJHMACGEJHYRSNJSWASHYESGYWSA")
    cipher_suite = Fernet(key)
    data = json.loads(cipher_suite.decrypt(code.encode('utf-8')))

    # Check exp
    now = datetime.datetime.utcnow().timestamp()
    if now > data['exp']:
        return Response(
            data={
                "details": "Error",
                "message": "Token expired",
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check for existence
    user = get_user_model().objects.filter(email=data['aud'])
    if not user.exists():
        return Response(
            data={
                "details": "Error",
                "message": "Email not found",
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # TODO: Activate account
    user = user.first()

    return Response(
        data={
            "details": "Ok",
            "message": "Account Activated",
            # ! For testing purposes only - should be removed
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_recover(request):
    """
        Take in email and send a token for recovering account
    """
    email = request.POST.get('email')
    userFilter = get_user_model().objects.filter(email=email)

    # Check for existence
    if userFilter.exists():
        user = userFilter.first()
        payload = {
            "email": user.email,
            "cur_password": user.password,
            "exp": datetime.datetime.timestamp(datetime.datetime.utcnow() + datetime.timedelta(days=1)),
            "iat": datetime.datetime.timestamp(datetime.datetime.utcnow()),
        }
        recover_token = jwt.encode(
            payload, settings.SECRET_KEY, algorithm='HS256')
        return Response(
            data={
                "details": "Ok",
                "recover_token": recover_token,
            },
            status=status.HTTP_200_OK
        )

    return Response(
        data={
            "details": "Error",
            "message": "Email not found",
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def recover_user(request):
    """
        Take in a token and new password, verify the token and change the password of the account encrypted in the token to the new one
    """
    recover_token = request.POST.get('code')
    new_password = request.POST.get('new_password')
    data = jwt.decode(recover_token, settings.SECRET_KEY, algorithms='HS256')

    # Check exp
    if datetime.datetime.now().timestamp() > data['exp']:
        return Response(
            data={
                "details": "Error",
                "message": "Token has expired"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user = get_user_model().objects.get(email=data['email'])

    # Check current password
    if user.password != data['cur_password']:
        return Response(
            data={
                "details": "Error",
                "message": "Invalid token"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # TODO: Update password of the user in database
    # ! This does not update the user state in db, still in production
    user.password = new_password

    return Response(
        data={
            "details": "Ok",
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def list_user(request):
    """
        Return list of users with a specified view
    """
    filterParam = {  # ! Hardcoding: View permissions for list
        "uuid": False,
        "uid": False,
        "first_name": True,
        "last_name": True,
        "birth_date": True,
        "email": True,
        "mobile": True,
        "male": True,
        "password": False,
        "address": True,
        "role_id": True,
        "avatar": True,
        "created_at": False,
        "updated_at": False,
    }

    listZ = []
    for key in filterParam:  # Query filter for choosing views
        if filterParam[key]:
            listZ.append(key)

    # Asterisk expands list into separated args
    # https://docs.python.org/2/tutorial/controlflow.html#unpacking-argument-lists
    data = get_user_model().objects.all().values(*listZ)
    return Response(data)
