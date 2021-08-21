from django.contrib.auth import get_user_model

from rest_framework import (exceptions, status)
from rest_framework.permissions import AllowAny  # TODO Remove
from rest_framework.response import Response
from rest_framework.views import APIView

from master_api.utils import (get_by_uuid, convert_time)
from master_api.views import (
    create_object, edit_object, delete_object, get_object
)
from master_db.models import (ClassMetadata, Calendar)
from master_db.serializers import CalendarSerializer

CustomUser = get_user_model()


class CalendarView(APIView):
    permission_classes = [AllowAny]  # TODO Remove

    def post(self, request):
        return create_object(Calendar, data=request.data)

    def get(self, request):
        return get_object(Calendar, data=request.GET)

    def patch(self, request):
        return edit_object(Calendar, data=request.data)

    def delete(self, request):
        return delete_object(Calendar, data=request.data)


class FindCalendarView(APIView):
    permission_classes = [AllowAny]  # TODO Remove

    def get(self, request):
        """
            Take in user_uuid (optional).

            If user_uuid is provided, result will be all calendars for that user.

            If none, result will be all Calendars in db.
        """

        # user_uuid is provided
        user = request.GET.get('user_uuid')
        if user is not None:
            user = get_by_uuid(CustomUser, user)
            return Response(
                CalendarSerializer(user.calendar_set, many=True).data
            )

        # None are provided
        return Response(
            CalendarSerializer(Calendar.objects.all(), many=True).data
        )
