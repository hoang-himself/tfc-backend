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

    def get(self, request):
        # TODO
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def patch(self, request):
        # TODO
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def delete(self, request):
        # TODO
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
