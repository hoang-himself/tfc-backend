from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, ParseError


from master_db.models import CustomUser, ClassMetadata, Schedule, Session
from master_db.serializers import SessionSerializer
from master_api.utils import get_object_or_404, model_full_clean, formdata_bool, get_list_or_404

import datetime

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def add_session(request):
    """
        Take in sched_id, student_uuid, status.
    """
    # Get sched
    sched = get_object_or_404(Schedule, 'Schedule',
                              pk=request.POST.get('sched_id'))

    # Get student
    try:
        student = get_object_or_404(
            CustomUser, 'Student', uuid=request.POST.get('student_uuid'))
    except ValidationError as message:
        raise ParseError({'detail': list(message)})

    # Handle student not in sched's class
    if not sched.classroom in student.student_classes.all():
        raise ParseError(
            'Student does not belong to the class of this session')

    # Get model
    now = datetime.datetime.now().timestamp()
    session = Session(
        schedule=sched,
        student=student,
        status=formdata_bool(request.POST.get('status')),
        created_at=now,
        updated_at=now
    )

    # Validate model
    model_full_clean(session)

    # Save
    session.save()

    return Response(
        data={'details': 'Ok'},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def edit_session(request):
    """
        Take in student_uuid, sched_id, status.

        Change the student status to requested status.
    """
    # Get student
    try:
        session = get_object_or_404(Session, 'Session with the given student and schedule',
                                    student__uuid=request.POST.get(
                                        'student_uuid'),
                                    schedule__id=request.POST.get('sched_id')
                                    )
    except ValidationError as message:
        raise ParseError({'detail': list(message)})

    stat = formdata_bool(request.POST.get('status'))

    # Handle no content changed
    if session.status == stat:
        return Response(data={'detail': 'Same content'},
                        status=status.HTTP_204_NO_CONTENT
                        )

    # Change (formdata_bool ensures value return to be bool or None -> no need full clean)
    session.status = stat

    # Save
    session.save()

    return Response({'detail': 'Ok'})


@api_view(['GET'])
@permission_classes([AllowAny])
def list_session(request):
    """
        Take in class_name (optional), sched_id (optional), student_uuid (optional).

        If class_name is provided return all sessions in the class.

        If sched_id is provided return all sessions in the schedule.

        If student_uuid is provided return all sessions of the student.

        If none is provided return all sessions in the db.

        Priority: class_name > sched_id > student_uuid
    """
    # class_name is provided
    session = request.GET.get('class_name')
    if session is not None:
        session = get_list_or_404(
            Session, 'Class', session__classroom__name=session)
        return Response(SessionSerializer(session, many=True).data)

    # sched_id is provided, no need to show session field
    session = request.GET.get('sched_id')
    if session is not None:
        session = get_list_or_404(Session, 'Schedule', session__id=session)
        return Response(SessionSerializer(session, many=True).exclude_field('session').data)

    # student_uuid is provided, no need to show student field
    session = request.GET.get('student_uuid')
    if session is not None:
        try:
            session = get_list_or_404(
                Session, 'Student', student__uuid=session)
        except ValidationError as message:
            raise ParseError({'detail': list(message)})
        return Response(SessionSerializer(session, many=True).exclude_field('student').data)

    return Response(SessionSerializer(Session.objects.all(), many=True).data)
