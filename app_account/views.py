from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from master_db.models import user, role
from master_api import serializers

import re
import datetime

# Create your views here.


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def hello_world(request):
    hello = {
        "message": "Hello World!",
    }
    return Response(data=hello, status=200)


def emailValidate(email):
    # Validating email address
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
    if re.search(regex, email):
        return True
    else:
        return False


@api_view(['POST'])
@permission_classes([AllowAny])
def emailCheck(request):
    email = request.POST.get('email')
    # Validating email address
    if not emailValidate(email):
        return Response(
            data={
                "details": "Error",
                "message": "Invalid email address"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check for existence
    if user.objects.filter(email=email).exists():
        return Response(
            data={
                "details": "Ok",
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
        
def mobileValidate(mobile):
    # Validating mobile phone number
    regex = '/^(0?)(3[2-9]|5[6|8|9]|7[0|6-9]|8[0-6|8|9]|9[0-4|6-9])[0-9]{7}$/'
    if re.search(regex, mobile):
        return True
    else:
        return False
        
@api_view(['POST'])
@permission_classes([AllowAny])
def mobileCheck(request):
    mobile = request.POST.get('mobile')
    # Validating mobile address
    if not mobileValidate(mobile):
        return Response(
            data={
                "details": "Error",
                "message": "Invalid mobile phone number "
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check for existence
    if user.objects.filter(mobile=mobile).exists():
        return Response(
            data={
                "details": "Ok",
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
def create_user(request):
    """
        Insignificant factors:
        - These factors are freely defined and do not affect
        its corresponding account if input incorrectly.
    """
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    address = request.POST.get('address')
    male = request.POST.get('male')
    avatar = request.POST.get('avatar')
    birth_date = request.POST.get('birth_date')
    created_at = datetime.datetime.now().timestamp()
    updated_at = created_at
    uid = 'something'
    uuid = 'something'

    """
        Significant factors:
        - These are the oposite of the insignificant factors,
        they greately affect the user account.
        There must be a strict rule for these to obey.
    """
    # Verify email address
    email = emailCheck(request)
    if email.status == status.HTTP_400_BAD_REQUEST:
        return Response(
            data={
                "details": "Error",
                "message": email.data["message"],
            }
        )
    else:
        email = request.POST.get('email')
        
    mobile = mobileCheck(request)
    if mobile.status == status.HTTP_400_BAD_REQUEST:
        return Response(
            data={
                "details": "Error",
                "message": mobile.data["message"],
            }
        )
    else:
        mobile = request.POST.get('email')
        
    password = request.POST.get('password')

    newUser = user(
        uuid=uuid,
        uid=uid,
        first_name=first_name,
        last_name=last_name,
        birth_date=birth_date,
        email=email,
        mobile=mobile,
        male=male,
        password=password,
        address=address,
        avatar=avatar,
        created_at=created_at,
        updated_at=updated_at,
    )

    response = Response()
    return response


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def viewUser(request):
    users = user.objects.all()
    serializer = serializers.UserSerializer(users, many=True)
    return Response(serializer.data)
