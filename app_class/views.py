from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from rest_framework import (exceptions, status)
from rest_framework.response import Response
from rest_framework.serializers import RelatedField
from rest_framework.views import APIView

from master_api.utils import get_by_uuid
from master_api.views import get_object, create_object, delete_object, edit_object
from master_db.models import CustomUser, ClassMetadata, Course
from master_db.serializers import ClassMetadataSerializer, CourseSerializer

import json

CustomUser = get_user_model()


class ClassView(APIView):
    def post(self, request):
        return create_object(ClassMetadata, data=request.data)

    def get(self, request):
        return get_object(ClassMetadata, data=request.GET)

    def patch(self, request):
        return edit_object(ClassMetadata, data=request.data)

    def delete(self, request):
        return delete_object(ClassMetadata, data=request.data)


class ClassStudentView(APIView):
    # This is for adding student
    def patch(self, request):
        """
            Take in uuid, student_uuids. Param uuid represents class
            with the given uuid, student_uuids is a list of student's
            uuid

            Param student_uuids must be in the form of: uuid1, uuid2,
            uuid3 (whitespace is optional)
        """
        CustomUser = get_user_model()

        # Get class
        classMeta = get_by_uuid(ClassMetadata, request.POST.get('uuid'))

        # Get all students with uuids
        if (std_uuids := request.POST.get('student_uuids')) is None:
            raise exceptions.ParseError(
                {'student_uuids': 'This field is required.'}
            )

        std_uuids = json.loads(std_uuids)
        # Handling UUID validation
        try:
            db = CustomUser.objects.filter(uuid__in=std_uuids)
        except ValidationError as message:
            raise exceptions.ParseError({'details': list(message)})

        # Store students id for adding
        students = db.values_list('pk', flat=True)
        # Store uuids for visualizing added students, if one does not show up it is not found
        uuids = db.values_list('uuid', flat=True)

        # Add students
        classMeta.students.add(*students)
        if bool(uuids):
            classMeta.save()

        return Response({'students_added': uuids})

    def delete(self, request):
        """
            Take in uuid and student_uuids. Param uuid represents class
            with the given uuid, student_uuids is a list of student uuid.

            Every uuid in student_uuids must be a valid student or else
            removal will not be performed.

            Param student_uuids must be in the form of: uuid1, uuid2,
            uuid3 (whitespace is optional)
        """

        # Get class
        classMeta = get_by_uuid(ClassMetadata, request.POST.get('uuid'))

        # Get students uuids
        if (std_uuids := request.POST.get('student_uuids')) is None:
            raise exceptions.ParseError(
                {'student_uuids': 'This field is required.'}
            )
        std_uuids = json.loads(std_uuids)
        # Get students
        try:
            students = classMeta.students.filter(uuid__in=std_uuids)
        except ValidationError as message:
            raise exceptions.ParseError({'details': list(message)})

        # Store uuids for visualizing added students, if one does not show up it is not found
        if len(students) != len(std_uuids):
            uuids = (
                str(o) for o in students.values_list('uuid', flat=True).filter()
            )
            raise exceptions.ParseError(
                {'not_found': list(set(std_uuids).difference(uuids))}
            )

        # Remove students from class if all uuids are present
        classMeta.students.remove(*students)
        classMeta.save()

        return Response({'details': 'Ok'})


class CourseRelatedField(RelatedField):
    def to_representation(self, obj):
        return CourseSerializer(obj).ignore_fields('created', 'modified').data


class SpecialClassSerializer(ClassMetadataSerializer):
    course = CourseRelatedField(read_only=True)


class FindClassView(APIView):
    def get(self, request):
        """
            Take in course_uuid (optional),student_uuid (optional), teacher_uuid (optional).
            Param student_uuid represents uuid of a student.

            If course_uuid is provided return all classes of the given
            course (No explicit info of students, just number of students).

            If student_uuid is provided return all classes of the given
            student (No explicit info of students, just number of students).

            If teacher_uuid is provided return all classes of the given
            teacher (No explicit info of students, just number of students).

            If none is provided return all classes in db with similar
            format of student_uuid.
        """
        classMeta = ClassMetadata.objects.all()

        # course_uuid is provided
        course_uuid = request.GET.get('course_uuid')
        if course_uuid is not None:
            # Get course by uuid
            course = get_by_uuid(Course, course_uuid)
            classMeta = course.classmetadata_set.all()

        # student_uuid is provided
        student_uuid = request.GET.get('student_uuid')
        if student_uuid is not None:
            # Get student by uuid
            student = get_by_uuid(CustomUser, student_uuid)
            classMeta = student.student_classes.all()
            return Response(
                SpecialClassSerializer(classMeta,
                                       many=True).ignore_field('students').data
            )

        # teacher_uuid is provided
        teacher_uuid = request.GET.get('teacher_uuid')
        if teacher_uuid is not None:
            # Get teacher by uuid
            teacher = get_by_uuid(CustomUser, teacher_uuid)
            classMeta = teacher.teacher_classes.all()

        data = ClassMetadataSerializer(classMeta,
                                       many=True).ignore_field('students').data

        return Response(data)
