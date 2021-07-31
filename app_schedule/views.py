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
from master_db.models import ClassMetadata, Schedule
from master_db.serializers import ScheduleSerializer


CustomUser = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def create_sched(request):
    return create_object(Schedule, data=request.data)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def edit_sched(request):
    return edit_object(Schedule, data=request.data)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_sched(request):
    return delete_object(Schedule, data=request.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sched(request):
    return get_object(Schedule, data=request.GET)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_sched(request):
    """
        Take in class_uuid (optional), student_uuid (optional), teacher_uuid (optional).

        If class_uuid is provided, result will be all schedules for that class.

        If student_uuid is provided, result will be all schedules for all the classes that have that student

        If none, result will be all schedules in db.

        Priority: class_uuid > student_uuid > teacher_uuid
    """

    # class_uuid is provided
    classMeta = request.GET.get('class_uuid')
    if classMeta is not None:
        classMeta = get_by_uuid(ClassMetadata, classMeta)
        return Response(ScheduleSerializer(classMeta.schedule_set, many=True).data)

    # student_uuid is provided
    student = request.GET.get('student_uuid')
    if not student is None:
        # Get student
        student = get_by_uuid(CustomUser, student)

        # Get classes of student
        classes = student.student_classes.all()

        # Iterate through each class and get its schedules
        data = []
        for c in classes:
            data.extend(ScheduleSerializer(c.schedule_set, many=True).data)

        return Response(data)

    # teacher_uuid is provided
    teacher = request.GET.get('teacher_uuid')
    if not teacher is None:
        # Get student
        teacher = get_by_uuid(CustomUser, teacher)

        # Get classes of teacher
        classes = teacher.teacher_classes.all()

        # Iterate through each class and get its schedules
        data = []
        for c in classes:
            data.extend(ScheduleSerializer(c.schedule_set, many=True).data)

        return Response(data)

    # None are provided
    return Response(ScheduleSerializer(Schedule.objects.all(), many=True).data)
