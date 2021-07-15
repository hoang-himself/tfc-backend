from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_protect

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app_auth.utils import request_to_userobj
from master_db.serializers import CustomUserSerializer

import datetime
import re

CustomUser = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def get_self(request):
    user = request_to_userobj(request)
    user = CustomUserSerializer(user)

    filter_query = request.GET.getlist('filter')

    # Asterisk expands list into separated args
    # https://docs.python.org/2/tutorial/controlflow.html#unpacking-argument-lists
    data = CustomUser.objects.get(uuid=user['uuid'].value)
    data = CustomUserSerializer(data).data
    if filter_query:
        data = {key: data[key] for key in filter_query}
    return Response(data=data, status=status.HTTP_200_OK)


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


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def list_user(request):
    """
        Return list of users with a specified view
    """
    filter_query = request.GET.getlist('filter')

    if not filter_query:
        filter_query = [
            'uuid',
            'email',
            'first_name',
            'last_name',
            'birth_date',
            'mobile',
            'male',
            'address',
            'is_active',
            'last_login',
            'date_joined',
            'date_updated',
        ]

    filter_dict = {
        'uuid': True,
        'email': True,
        'first_name': True,
        'last_name': True,
        'birth_date': True,
        'mobile': True,
        'male': True,
        'address': True,
        'avatar': False,
        # 'role__name': True,
        'is_active': True,
        'last_login': True,
        'date_joined': True,
        'date_updated': True,
    }

    # TODO
    listZ = []
    for key in filter_query:  # Query filter for choosing views
        if filter_dict[key]:
            listZ.append(key)

    # Asterisk expands list into separated args
    # https://docs.python.org/2/tutorial/controlflow.html#unpacking-argument-lists
    data = CustomUser.objects.all().values(*listZ)
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
# @csrf_protect
def create_user(request) -> Response:
    """
        Requires every param: first_name, last_name, address, male, avatar, birth_date, role_id, email, mobile, username, password.

        The role_id param takes in int type and represents the id of the group in database.
    """
    # TODO
    # Insignificant factors:
    # - These factors are freely defined and do not affect
    # its corresponding account if input incorrectly.

    # check = has_perm(request, ['account_cred'])
    # if check.status_code >= 400:
    #     return check

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
    password = request.POST.get('password')

    # Verify email address
    check = email_response(email)
    if check.status_code == status.HTTP_400_BAD_REQUEST:
        return check

    # Verify mobile phone number
    check = mobile_response(mobile)
    if check.status_code == status.HTTP_400_BAD_REQUEST:
        return check

    # Verify password
    check = password_response(password)
    if check.status_code == status.HTTP_400_BAD_REQUEST:
        return check

    # DB generated factor:
    # - These are generated automatically and seperated from
    # user input

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
        # username=username,
        first_name=first_name,
        last_name=last_name,
        birth_date=birth_date,
        email=email,
        mobile=mobile,
        male=male,
        password=make_password(password),
        address=address,
        # group=group,
        avatar=avatar,
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


@api_view(['PATCH'])
@permission_classes([AllowAny])
@csrf_protect
def edit_user(request):
    # TODO
    pass


@api_view(['DELEte'])
@permission_classes([AllowAny])
@csrf_protect
def delete_user(request):
    # TODO
    pass


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def list_staff(request):
    # TODO
    pass


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def create_staff(request):
    """
        Return list of users with a specified view
    """
    # TODO
    filter_query = request.GET.getlist('filter')

    if not filter_query:
        filter_query = [
            'uuid',
            'email',
            'first_name',
            'last_name',
            'birth_date',
            'mobile',
            'male',
            'address',
            'is_active',
            'last_login',
            'date_joined',
            'date_updated',
        ]

    filter_dict = {
        'uuid': True,
        'email': True,
        'first_name': True,
        'last_name': True,
        'birth_date': True,
        'mobile': True,
        'male': True,
        'address': True,
        'avatar': False,
        'date_joined': True,
        # 'role__name': True,
        'is_active': True,
        'last_login': True,
        'date_joined': True,
        'date_updated': True,
    }

    # TODO
    listZ = []
    for key in filter_query:  # Query filter for choosing views
        if filter_dict[key]:
            listZ.append(key)

    # Asterisk expands list into separated args
    # https://docs.python.org/2/tutorial/controlflow.html#unpacking-argument-lists
    data = CustomUser.objects.all().values(*listZ)
    return Response(data)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def edit_staff(request):
    # TODO
    pass


@api_view(['DELETE'])
@permission_classes([AllowAny])
@csrf_protect
def delete_staff(request):
    # TODO
    pass
