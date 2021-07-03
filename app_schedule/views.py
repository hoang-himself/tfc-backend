from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, ParseError


from app_auth.utils import has_perm
from master_db.models import MyUser, ClassMetadata, Schedule
from master_db.serializers import ScheduleSerializer
from master_api.utils import get_object_or_404, model_full_clean, edit_object


import datetime

def validate_sched(sched):
    model_full_clean(sched)

    # Validate time
    time_start, time_end = sched.time_start, sched.time_end
    if time_end <= time_start:
        raise ParseError('Time end must be greater than time start')

    return None


@api_view(['POST'])
@permission_classes([AllowAny])
def create_sched(request):
    """
        Take in class_name, time_start, time_end, time_end must be greater than time_start and both are int
    """
    # Get class
    classroom = get_object_or_404(
        ClassMetadata, 'Class', name=request.POST.get('class_name'))

    # Get model
    time_start = request.POST.get('time_start')
    time_end = request.POST.get('time_end')
    now = datetime.datetime.now().timestamp()
    sched = Schedule(
        classroom=classroom,
        time_start=time_start,
        time_end=time_end,
        created_at=now,
        updated_at=now
    )

    # Validate model
    validate_sched(sched)

    # Save
    sched.save()

    return Response(
        data={
            # ! For testing purposes only, should be removed
            'data': ScheduleSerializer(sched).data
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def edit_sched(request):
    """
        Take in target_id, classroom (optional), time_start (optional), time_end (optional). time_start and time_end must be integers.

        The optional params if not provided will not be updated. If the content provided is the same as the source, no change will be made.

        If at least one optional param is provided, updated_at will be updated.
    """
    # Get params and convert some to int
    modifiedDict = request.POST.copy()
    if not modifiedDict.get('time_start') is None:
        modifiedDict['time_start'] = int(modifiedDict['time_start'])
    if not modifiedDict.get('time_end') is None:
        modifiedDict['time_end'] = int(modifiedDict['time_end'])

    # Get schedule
    sched = get_object_or_404(Schedule, 'Schedule',
                              pk=modifiedDict.get('target_id'))

    # Get classroom if necessary
    if not modifiedDict.get('classroom') is None:
        modifiedDict['classroom'] = get_object_or_404(
            ClassMetadata, 'Class', name=modifiedDict['classroom'])

    # Make changes
    modifiedList = []
    edit_object(sched, modifiedDict, modifiedList)

    # If changed update updated_at
    if bool(modifiedList):
        sched.updated_at = datetime.datetime.now().timestamp()
        modifiedList.append('updated_at')

    # Validate model
    validate_sched(sched)

    # Save
    sched.save()

    return Response(
        data={
            'modified': modifiedList,
        }
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_sched(request):
    """
        Take in id and delete sched with the following id.
    """
    get_object_or_404(Schedule, 'Schedule', pk=request.POST.get('id')).delete()
    return Response(
        data={'detail': 'Ok'},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_sched(request):
    classMeta = request.GET.get('class_name')
    if not classMeta is None:
        classMeta = get_object_or_404(ClassMetadata,'Class', name=classMeta)
        return Response(ScheduleSerializer(classMeta.schedule_set, many=True).data)
    
    student = request.GET.get('student_uuid')
    if not student is None:
        try:
            student = get_object_or_404(MyUser, 'Student', uuid=student)
        except ValidationError as message:
            raise ParseError({'detail': list(message)})
        
        classes = student.student_classes.all()
        data = []
        for c in classes:
            data.extend(ScheduleSerializer(c.schedule_set, many=True).data)
            
        return Response(data)
    
    raise ParseError('Need parameter class_name or student_uuid')