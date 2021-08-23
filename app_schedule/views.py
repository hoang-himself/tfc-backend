from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework.views import APIView

from master_api.utils import get_by_uuid
from master_api.views import (
    create_object, edit_object, delete_object, get_object
)
from master_db.models import (ClassMetadata, Schedule)
from master_db.serializers import ScheduleSerializer

CustomUser = get_user_model()


class ScheduleView(APIView):
    def post(self, request):
        return create_object(Schedule, data=request.data)

    def get(self, request):
        return get_object(Schedule, data=request.GET)

    def patch(self, request):
        return edit_object(Schedule, data=request.data)

    def delete(self, request):
        return delete_object(Schedule, data=request.data)


class FindScheduleView(APIView):
    def get(self, request):
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
            return Response(
                ScheduleSerializer(classMeta.schedule_set, many=True).data
            )

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
        return Response(
            ScheduleSerializer(Schedule.objects.all(), many=True).data
        )
