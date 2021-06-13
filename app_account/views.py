from django.conf import settings

from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from master_db.models import User, Role
from master_api.serializers import UserSerializer

import re
import datetime
import uuid as uuid_gen
import json
import jwt
import hashlib
import base64
from cryptography.fernet import Fernet

# Create your views here.


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def hello_world(request):
    hello = {
        "message": "Hello World!",
    }
    return Response(data=hello, status=200)


def emailValidate(email):
    # Check nullity
    if email is None:
        return False
    
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
    # Check nullity
    if mobile is None:
        return False

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
def usernameCheck(request):
    uid = request.POST.get('uid')
    return usernameResponse(uid)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    """
        Requires every param: first_name, last_name, address, male, avatar, birth_date, role_id, email, mobile, uid, password.
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
    role_id = request.POST.get('role_id')

    # Significant factors:
    # - These are the oposite of the insignificant factors,
    # they greately affect the user account.
    # There must be a strict rule for these to obey.
    
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
    
    #TODO: Handling password
    
    
    
    # DB generated factor:
    # - These are generated automatically and seperated from
    # user input
    
    created_at = datetime.datetime.now().timestamp()
    updated_at = created_at
    uuid = uuid_gen.uuid4()
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
        role_id=role,
    )
    
    dictionary = UserSerializer(newUser, many=False)
    serializer = UserSerializer(data=dictionary.data)
    
    if serializer.is_valid(raise_exception=True): # If required fields are empty function returns Django implemented exception
        # TODO: Save the user
        #serializer.save()
        return Response(
                data={
                    "details": "Ok",
                    "message": "Successfully created",
                    "user": serializer.data, #! Just use for testing
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
        
def tokenGenerator(email):
    payload = {
        'aud': email,
    }
    token = jwt.encode(payload, "secret", algorithm='HS256')
    return token

@api_view(['GET'])
@permission_classes([AllowAny])
def sendActivation(request):
    email = request.GET.get('email')
    
    # Check for existence
    if not User.objects.filter(email=email).exists():
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
    
    #TODO: Encrypt data
    data = json.dumps(data).encode('utf-8')
    key = base64.urlsafe_b64encode(b"PBKDFJHMACGEJHYRSNJSWASHYESGYWSA") #! Hardcoding: A byte-like string with length = 32
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
    code = request.GET.get('code')
    
    #TODO: Decrypt data
    key = base64.urlsafe_b64encode(b"PBKDFJHMACGEJHYRSNJSWASHYESGYWSA") #! Hardcoding: A byte-like string with length = 32
    cipher_suite = Fernet(key)
    data = json.loads(cipher_suite.decrypt(code.encode('utf-8')))
    
    now = datetime.datetime.utcnow().timestamp()
    if now < data['exp']:
        exp = 'Still acceptable'
    else:
        exp = 'Already expired'
    
    if User.objects.filter(email=data['aud']).exists():
        exist = 'This account can be activated'
    else:
        exist = 'Account not found'
    
    #TODO: Activate account
    
    return Response(
        data={
            "exp": exp,
            "exist": exist,
            "data": data,
        },
        status=status.HTTP_200_OK
    )
    

@api_view(['POST'])
@permission_classes([AllowAny])
def sendRecover(request):
    email = request.POST.get('email')
    print(email)
    userFilter = User.objects.filter(email=email)
    print(userFilter.exists())
    if userFilter.exists():
        user = userFilter.first()
        payload = {
            "email": user.email,
            "cur_password": user.password,
            "exp": datetime.datetime.timestamp(datetime.datetime.utcnow() + datetime.timedelta(days=1)),
            "iat": datetime.datetime.timestamp(datetime.datetime.utcnow()),
        }
        recover_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
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
def recoverUser(request):
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
        
    user = User.objects.get(email=data['email'])
        
    # Check current password
    if user.password != data['cur_password']:
        return Response(
            data={
                "details": "Error",
                "message": "Invalid token"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
    #TODO: Update password of the user in database
    user.password = new_password #! This does not update the user state in db, still in production 
    
    return Response(
        data={
            "details": "Ok",
            "user": UserSerializer(user).data,
        },
        status=status.HTTP_200_OK
    )

    
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def listUser(request):
    Users = User.objects.all()
    serializer = UserSerializer(Users, many=True)
    return Response(serializer.data)