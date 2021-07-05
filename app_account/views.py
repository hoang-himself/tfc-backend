from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError


from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from app_auth.utils import has_perm
from master_db.models import CustomUser
from master_db.serializers import CustomUserSerializer

import re
import datetime

# Create your views here.


def email_validate(email) -> bool:
    """
        Validate email address format
    """
    # Check nullity
    if email is None or email == '':
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
    if CustomUser.objects.filter(email=email).exists():
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
    if mobile is None or mobile == '':
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
                "message": "Invalid mobile phone number"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check for existence
    if CustomUser.objects.filter(mobile=mobile).exists():
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


def username_response(username) -> Response:
    """
        Return response when checking signed up username in db
    """
    # Check nullity
    if username is None or username == '':
        return Response(
            data={
                "details": "Error",
                "message": "Username cannot be empty"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check for existence
    if CustomUser.objects.filter(username=username).exists():
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
    username = request.POST.get('username')
    return username_response(username)


def password_validate(password):
    """
        Validate password format
    """
    regex = '[A-Za-z0-9@#$%^&+=]{8,}'
    if re.fullmatch(regex, password):
        return True
    else:
        return False


def password_response(password) -> Response:
    """
        Return response when checking password strength
    """
    # Check nullity
    if password is None or password == '':
        return Response(
            data={
                "details": "Error",
                "message": "Password cannot be empty"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validating password
    if not password_validate(password):
        return Response(
            data={
                "details": "Error",
                "message": "Password is too short"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        return Response(
            data={
                "details": "Ok",
                "message": "Password is suitable for creating user"
            },
            status=status.HTTP_200_OK
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def password_check(request) -> Response:
    """
        API for checking password strength
    """
    password = request.POST.get('password')
    return Response(password)


@api_view(['POST'])
@permission_classes([AllowAny])
# @csrf_protect
def create_user(request) -> Response:
    """
        Requires every param: first_name, mid_name, last_name, address, male, avatar, birth_date, role_id, email, mobile, username, password.

        The role_id param takes in int type and represents the id of the group in database.
    """

    # Insignificant factors:
    # - These factors are freely defined and do not affect
    # its corresponding account if input incorrectly.

    # check = has_perm(request, ['account_cred'])
    # if check.status_code >= 400:
    #     return check

    first_name = request.POST.get('first_name')
    mid_name = request.POST.get('mid_name')
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
        return check

    # Verify mobile phone number
    check = mobile_response(mobile)
    if check.status_code == status.HTTP_400_BAD_REQUEST:
        return check

    # Verify username
    check = username_response(username)
    if check.status_code == status.HTTP_400_BAD_REQUEST:
        return check

    # Verify password
    check = password_response(password)
    if check.status_code == status.HTTP_400_BAD_REQUEST:
        return check

    # DB generated factor:
    # - These are generated automatically and seperated from
    # user input

    created_at = datetime.datetime.now().timestamp()
    updated_at = created_at
    # group = request.POST.get('group')

    # Get group from group_id
    # group = MyGroup.objects.filter(name=group)
    # if group.exists():
    #     group = group.first()
    # else:
    #     return Response(
    #         data={
    #             'details': 'Error',
    #             'message': 'Group does not exist'
    #         },
    #         status=status.HTTP_400_BAD_REQUEST
    #     )

    #
    user = CustomUser(
        username=username,
        first_name=first_name,
        mid_name=mid_name,
        last_name=last_name,
        birth_date=birth_date,
        email=email,
        mobile=mobile,
        male=male,
        password=make_password(password),
        address=address,
        # group=group,
        avatar=avatar,
        created_at=created_at,
        updated_at=updated_at,
    )

    try:
        user.full_clean()
    except ValidationError as message:
        return Response(
            data={
                'details': 'Error',
                'message': message
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    user.save()

    return Response(
        data={
            "details": "Ok",
            "message": "User created",
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
# @csrf_protect
def list_user(request):
    """
        Return list of users with a specified view
    """
    # check = has_perm(request, ['account_cred'])
    # if check.status_code >= 400:
    #     return check

    filter_query = request.GET.getlist('filter')

    if not filter_query:
        filter_query = [
            'pk',
            'uuid',
            'username',
            'first_name',
            'mid_name',
            'last_name',
            'email',
            'birth_date',
            'mobile',
            'male',
            'address',
            # 'role__name',
            'is_active',
            'created_at',
            'updated_at'
        ]

    filter_dict = {
        'pk': True,
        'uuid': True,
        'username': True,
        'first_name': True,
        'mid_name': True,
        'last_name': True,
        'email': True,
        'password': False,
        'birth_date': True,
        'mobile': True,
        'male': True,
        'address': True,
        'avatar': False,
        # 'role__name': True,
        'is_active': True,
        'created_at': True,
        'updated_at': True
    }

    listZ = []
    for key in filter_query:  # Query filter for choosing views
        if filter_dict[key]:
            listZ.append(key)

    # Asterisk expands list into separated args
    # https://docs.python.org/2/tutorial/controlflow.html#unpacking-argument-lists
    data = CustomUser.objects.all().values(*listZ)
    return Response(data)
