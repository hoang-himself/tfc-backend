from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_protect

from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from master_api.utils import get_by_uuid, convert_time
from master_api.views import create_object, edit_object, delete_object, get_object
from master_db.models import ClassMetadata, Calendar
from master_db.serializers import CalendarSerializer


CustomUser = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def create_calendar(request):
    return create_object(Calendar, data=request.data)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def edit_calendar(request):
    return edit_object(Calendar, data=request.data)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_calendar(request):
    return delete_object(Calendar, data=request.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_calendar(request):
    return get_object(Calendar, data=request.GET)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_calendar(request):
    """
        Take in user_uuid (optional).

        If user_uuid is provided, result will be all calendars for that user.

        If none, result will be all Calendars in db.
    """

    # user_uuid is provided
    user = request.GET.get('user_uuid')
    if user is not None:
        user = get_by_uuid(CustomUser, user)
        return Response(CalendarSerializer(user.calendar_set, many=True).data)

    # None are provided
    return Response(CalendarSerializer(Calendar.objects.all(), many=True).data)
