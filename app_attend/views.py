from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, ParseError


from app_auth.utils import has_perm
from master_db.models import MyUser, ClassMetadata, Schedule, Attendance
from master_db.serializers import AttendanceSerializer
from master_api.utils import get_object_or_404, model_full_clean, formdata_bool, get_list_or_404

import datetime

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def add_attend(request):
    """
        Take in sched_id, student_uuid, status.
    """
    # Get sched
    sched = get_object_or_404(Schedule, 'Schedule',
                              pk=request.POST.get('sched_id'))

    # Get student
    try:
        student = get_object_or_404(
            MyUser, 'Student', uuid=request.POST.get('student_uuid'))
    except ValidationError as message:
        raise ParseError({'detail': list(message)})

    # Handle student not in sched's class
    if not sched.classroom in student.student_classes.all():
        raise ParseError(
            'Student does not belong to the class of this session')

    # Get model
    now = datetime.datetime.now().timestamp()
    attend = Attendance(
        session=sched,
        student=student,
        status=formdata_bool(request.POST.get('status')),
        created_at=now,
        updated_at=now
    )

    # Validate model
    model_full_clean(attend)

    # Save
    attend.save()

    return Response(
        data={'details': 'Ok'},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def edit_attend(request):
    """
        Take in student_uuid, sched_id, status.

        Change the student status to requested status.
    """
    # Get student
    try:
        attend = get_object_or_404(Attendance, 'Attendance with the given student and schedule',
                                   student__uuid=request.POST.get('student_uuid'), session__id=request.POST.get('sched_id'))
    except ValidationError as message:
        raise ParseError({'detail': list(message)})

    stat = formdata_bool(request.POST.get('status'))

    # Handle no content changed
    if attend.status == stat:
        return Response(data={'detail': 'Same content'},
                        status=status.HTTP_204_NO_CONTENT
                        )

    # Change (formdata_bool ensures value return to be bool or None -> no need full clean)
    attend.status = stat

    # Save
    attend.save()

    return Response({'detail': 'Ok'})


@api_view(['GET'])
@permission_classes([AllowAny])
def list_attend(request):
    """
        Take in class_name (optional), sched_id (optional), student_uuid (optional).

        If class_name is provided return all attendances in the class.

        If sched_id is provided return all attendances in the schedule.

        If student_uuid is provided return all attendances of the student.

        If none is provided return all attendances in the db.

        Priority: class_name > sched_id > student_uuid
    """
    # class_name is provided
    attend = request.GET.get('class_name')
    if attend is not None:
        attend = get_list_or_404(
            Attendance, 'Class', session__classroom__name=attend)
        return Response(AttendanceSerializer(attend, many=True).data)

    # sched_id is provided, no need to show session field
    attend = request.GET.get('sched_id')
    if attend is not None:
        attend = get_list_or_404(Attendance, 'Schedule', session__id=attend)
        return Response(AttendanceSerializer(attend, many=True).exclude_field('session').data)

    # student_uuid is provided, no need to show student field
    attend = request.GET.get('student_uuid')
    if attend is not None:
        try:
            attend = get_list_or_404(
                Attendance, 'Student', student__uuid=attend)
        except ValidationError as message:
            raise ParseError({'detail': list(message)})
        return Response(AttendanceSerializer(attend, many=True).exclude_field('student').data)

    return Response(AttendanceSerializer(Attendance.objects.all(), many=True).data)
