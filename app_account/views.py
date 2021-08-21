from annoying.functions import get_object_or_None

from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import (exceptions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from master_api.views import (
    create_object, get_object, edit_object, delete_object
)
from master_db.serializers import CustomUserSerializer

import jwt

CustomUser = get_user_model()


class SelfView(APIView):
    def get(self, request):
        if not (authorization_header := request.headers.get('Authorization')):
            return None
        try:
            # header = 'Token xxxxxxxxxxxxxxxxxxxxxxxx'
            if not (access_token := authorization_header.split(' ')[1]):
                raise exceptions.PermissionDenied('Not logged in.')

            payload = jwt.decode(
                access_token, settings.JWT_KEY, algorithms=['HS256']
            )
            if payload.get('typ') != 'access':
                raise exceptions.ParseError('Invalid access token')
        except IndexError:
            raise exceptions.AuthenticationFailed('Token prefix missing')
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Access token expired')

        if (
            (user := get_object_or_None(CustomUser, uuid=payload.get('uuid')))
            is None
        ):
            raise exceptions.NotFound('User not found.')

        if not user.is_active:
            raise exceptions.NotFound('User inactive.')

        return Response(CustomUserSerializer(user).data)


class UserView(APIView):
    def post(self, request):
        return create_object(CustomUser, data=request.data)

    def get(self, request):
        return Response(
            CustomUserSerializer(CustomUser.objects.all(), many=True).data
        )

    def patch(self, request):
        return edit_object(CustomUser, data=request.data)

    def delete(self, request):
        return delete_object(CustomUser, data=request.data)


class StaffView(APIView):
    def post(self, request):
        # TODO
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def get(self, request):
        # TODO
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def patch(self, request):
        # TODO
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request):
        # TODO
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
