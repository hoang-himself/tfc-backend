from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app_auth.utils import request_header_to_userobj
from master_api.views import (
    create_object, get_object,
    edit_object, delete_object
)
from master_db.serializers import CustomUserSerializer

CustomUser = get_user_model()


class SelfView(APIView):
    def get(self, request):
        user = request_header_to_userobj(request)
        return Response(CustomUserSerializer(user).data)


class UserView(APIView):
    def post(self, request):
        return create_object(CustomUser, data=request.data)

    def get(self, request):
        return Response(
            CustomUserSerializer(
                CustomUser.objects.all(), many=True).data
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
