from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes


from app_auth.utils import has_perm
from master_db.models import MyUser, ClassMetadata, Schedule
from master_db.serializers import ScheduleSerializer

import datetime

@api_view(['POST'])
@permission_classes([AllowAny])
def create_sched(request):
    """
        Take in class_name, time_start, time_end, time_end must be greater than time_start
    """
    # Get class
    try:
        classroom = ClassMetadata.objects.get(name=request.POST.get('class_name'))
    except ClassMetadata.DoesNotExist:
        return Response(
            data={
                'details': 'Error',
                'message': 'Class does not exist'
            },
            status=status.HTTP_404_NOT_FOUND
        )

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

    try:
        sched.full_clean()
    except ValidationError as message:
        return Response(
            data={
                'details': 'Error',
                'message': dict(message)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
    # Validate time
    time_start, time_end = int(time_start), int(time_end)
    if time_end < time_start:
        return Response(
            data={
                'details': 'Error',
                'message': 'Time end must be greater than time start'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
    # Save
    sched.save()

    return Response(
        data={
            'details': 'Ok',
            # ! For testing purposes only, should be removed
            'data': ScheduleSerializer(sched).data
        },
        status=status.HTTP_201_CREATED
    )
    
@api_view(['GET'])
@permission_classes([AllowAny])
def list_sched(request):
    return Response(ScheduleSerializer(Schedule.objects.all(), many=True).data)