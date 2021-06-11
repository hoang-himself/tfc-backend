from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from master_db.models import User, Role
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
    
def emailResponse(email):
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
    if User.objects.filter(email=email).exists():
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
def emailCheck(request):
    email = request.POST.get('email')
    return Response(email)

def mobileValidate(mobile):
    # Validating mobile phone number
    regex = '^(0?)(3[2-9]|5[6|8|9]|7[0|6-9]|8[0-6|8|9]|9[0-4|6-9])[0-9]{7}$'
    if re.search(regex, mobile):
        return True
    else:
        return False

def mobileResponse(mobile):
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
    if User.objects.filter(mobile=mobile).exists():
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
def mobileCheck(request):
    mobile = request.POST.get('mobile')
    return mobileResponse(mobile)

def usernameResponse(uid):
    # Check for existence
    if User.objects.filter(uid=uid).exists():
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
def usernameCheck(request):
    uid = request.POST.get('uid')
    return usernameResponse(uid)

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
    if male == 'true':
        male = True
    avatar = request.POST.get('avatar')
    birth_date = request.POST.get('birth_date')
    created_at = datetime.datetime.now().timestamp()
    updated_at = created_at
    uuid = 'something'

    """
        Significant factors:
        - These are the oposite of the insignificant factors,
        they greately affect the user account.
        There must be a strict rule for these to obey.
    """
    # Verify email address
    email = request.POST.get('email')
    mobile = request.POST.get('mobile')
    uid = request.POST.get('uid')
    password = request.POST.get('password')
    
    # Verify email address
    check = emailResponse(email)
    if check.status_code == status.HTTP_400_BAD_REQUEST:
        return Response(
            data={
                "details": "Error",
                "message": check.data["message"],
            }
        )
        
    # Verify mobile phone number
    check = mobileResponse(mobile)
    if check.status_code == status.HTTP_400_BAD_REQUEST:
        return Response(
            data={
                "details": "Error",
                "message": check.data["message"],
            }
        )

    # Verify username
    check = usernameResponse(uid)
    if check.status_code == status.HTTP_400_BAD_REQUEST:
        return Response(
            data={
                "details": "Error",
                "message": check.data["message"]
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # # Working with password
    # password = request.POST.get('password')

    newUser = User(
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
    
    serializer = serializers.UserSerializer(data=newUser, many=False)
    if serializer.is_valid():
        serializer.save()
        return Response(
            data={
                "details": "Ok",
                "message": "Successfully created",
                "user": serializer.data
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            data={
                "details": "Error",
                "message": "Model is not valid, cannot save"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def viewUser(request):
    Users = User.objects.all()
    serializer = serializers.UserSerializer(Users, many=True)
    return Response(serializer.data)
