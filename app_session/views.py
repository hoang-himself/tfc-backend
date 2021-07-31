from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, ParseError


from master_db.models import Session
from master_db.serializers import SessionSerializer
from master_api.utils import get_list_or_404
from master_api.views import create_object, edit_object, delete_object, get_object

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def create_session(request):
    return create_object(Session, data=request.data)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_session(request):
    return delete_object(Session, data=request.data)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def edit_session(request):
    return edit_object(Session, data=request.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_session(request):
    return get_object(Session, data=request.GET)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_session(request):
    """
        Take in class_uuid (optional), schedule_uuid (optional), student_uuid (optional).

        If class_uuid is provided return all sessions in the class.

        If schedule_uuid is provided return all sessions in the schedule.

        If student_uuid is provided return all sessions of the student.

        If none is provided return all sessions in the db.

        Priority: class_uuid > schedule_uuid > student_uuid
    """
    # class_name is provided
    session = request.GET.get('class_uuid')
    if session is not None:
        try:
            session = get_list_or_404(
                Session, 'Class', schedule__classroom__uuid=session)
            return Response(SessionSerializer(session, many=True).data)
        except ValidationError as message:
            raise ParseError({'detail': list(message)})

    # sched_id is provided, no need to show session field
    session = request.GET.get('schedule_uuid')
    if session is not None:
        try:
            session = get_list_or_404(
                Session, 'Schedule', schedule__uuid=session)
        except ValidationError as message:
            raise ParseError({'detail': list(message)})
        return Response(SessionSerializer(session, many=True).data)

    # student_uuid is provided, no need to show student field
    session = request.GET.get('student_uuid')
    if session is not None:
        try:
            session = get_list_or_404(
                Session, 'Student', student__uuid=session)
        except ValidationError as message:
            raise ParseError({'detail': list(message)})
        return Response(SessionSerializer(session, many=True).data)

    return Response(SessionSerializer(Session.objects.all(), many=True).data)
