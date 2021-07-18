from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_protect

from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from master_api.utils import get_object_or_404, model_full_clean, edit_object, get_by_uuid
from master_db.models import CustomUser, ClassMetadata, Course
from master_db.serializers import ClassMetadataSerializer

import datetime


CustomUser = get_user_model()


def get_teacher_by_uuid(uuid):
    CustomUser = get_user_model()

    teacher = get_by_uuid(CustomUser, 'Teacher user', uuid)

    verify_teacher(teacher)
    return teacher


def get_std_by_uuids(klass, uuids):
    try:
        return klass.objects.filter(uuid__in=uuids)
    except ValidationError as message:
        raise ParseError({'details': list(message)})


def verify_teacher(user):
    # TODO: Verify user is a teacher
    if '0919877' in user.mobile:
        raise ParseError('User is not a teacher')


@api_view(['POST'])
@permission_classes([AllowAny])
def create_class(request):
    """
        Take in course_uuid, name, teacher_uuid (Optional), status (Need revision), student_uuids (Optional)

        Param student_uuids must be in form of: uuid1, uuid2, uuid3 (whitespace is optional)
    """
    CustomUser = get_user_model()

    std_uuids = request.POST.get('student_uuids')
    teacher = request.POST.get('teacher_uuid')

    # Get course corresponding to course_uuid
    course = get_object_or_404(
        Course, 'Course', uuid=request.POST.get('course_uuid'))

    # Get teacher if available
    if teacher is not None:
        teacher = get_teacher_by_uuid(teacher)

    # Construct model
    classMeta = ClassMetadata(
        course=course,
        name=request.POST.get('name'),
        teacher=teacher,
        status=request.POST.get('status'),
    )

    # Validate model
    model_full_clean(classMeta)

    # Get students from std_uuids
    if std_uuids is not None:
        # Handling UUID validation
        db = get_std_by_uuids(CustomUser, std_uuids)

        # Store students id for adding
        students = db.values_list('pk', flat=True)
        # Store uuids for visualizing added students, if one does not show up it is not found
        std_uuids = db.values_list('uuid', flat=True)

    # Save and add students (M2M field must be added this way to save)
    classMeta.save()
    if std_uuids is not None:
        classMeta.students.add(*students)

    return Response(
        data={
            'teacher_added': not teacher is None,
            'students_added': std_uuids
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def add_student(request):
    """
        Take in uuid, student_uuids. Param uuid represents class with the given uuid, student_uuids is a list of student's uuid

        Param student_uuids must be in the form of: uuid1, uuid2, uuid3 (whitespace is optional)
    """
    CustomUser = get_user_model()

    # Get class
    classMeta = get_by_uuid(
        ClassMetadata, 'Class', request.POST.get('uuid'))

    # Get all students with uuids
    std_uuids = request.POST.get('student_uuids')
    if std_uuids is None:
        raise ParseError({'student_uuids': ['This field is required.']})

    std_uuids = std_uuids.replace(' ', '').split(',')
    # Handling UUID validation
    db = get_std_by_uuids(CustomUser, std_uuids)

    # Store students id for adding
    students = db.values_list('pk', flat=True)
    # Store uuids for visualizing added students, if one does not show up it is not found
    uuids = db.values_list('uuid', flat=True)

    # Add students
    classMeta.students.add(*students)
    if bool(uuids):
        classMeta.save()

    return Response({'students_added': uuids})


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_student(request):
    """
        Take in uuid and student_uuids. Param uuid represents class with the given uuid, student_uuids is a list of student uuid.

        Every uuid in student_uuids must be a valid student or else removal will not be performed.

        Param student_uuids must be in the form of: uuid1, uuid2, uuid3 (whitespace is optional)
    """

    # Get class
    classMeta = get_by_uuid(
        ClassMetadata, 'Class', request.POST.get('uuid'))

    # Get students uuids
    try:
        std_uuids = request.POST.get(
            'student_uuids').replace(' ', '').split(',')
    except:
        raise ParseError({'student_uuids': ['This field is required.']})

    # Get students
    students = get_std_by_uuids(classMeta.students, std_uuids)

    # Store uuids for visualizing added students, if one does not show up it is not found
    if len(students) != len(std_uuids):
        uuids = (str(o)
                 for o in students.values_list('uuid', flat=True).filter())
        raise ParseError(
            {'not_found': list(set(std_uuids).difference(uuids))})

    # Remove students from class if all uuids are present
    classMeta.students.remove(*students)
    classMeta.save()

    return Response({'details': 'Ok'})


@api_view(['POST'])
@permission_classes([AllowAny])
def edit_class(request):
    """
        Take in uuid, course_uuid (optional), teacher_uuid (optional), course (optional), name (optional), status (optional).

        The optional params if not provided will not be updated. If the content provided is the same as the source, no change will be made.

        If at least one optional param is provided, updated_at will be updated
    """
    modifiedDict = request.POST.copy()
    modifiedDict.pop('students', None)
    modifiedDict.pop('created_at', None)
    modifiedDict.pop('updated_at', None)

    # Get class
    classMeta = get_by_uuid(
        ClassMetadata, 'Class', request.POST.get('uuid'))

    # Get teacher if provided
    if modifiedDict.get('teacher_uuid') is not None:
        modifiedDict['teacher'] = get_teacher_by_uuid(
            modifiedDict['teacher_uuid'])

    # Get course if provided
    if modifiedDict.get('course_uuid') is not None:
        modifiedDict['course'] = get_object_or_404(
            Course, 'Course', name=modifiedDict['course_uuid'])

    # Update the provided fields if content changed
    modifiedList = edit_object(classMeta, modifiedDict)

    if not modifiedList:
        return Response(data={'detail': 'modified nothing'}, status=status.HTTP_304_NOT_MODIFIED)
    else:
        modifiedList.append('modified')

    # Validate model
    model_full_clean(classMeta)

    # Save
    classMeta.save()

    return Response({'modified': modifiedList})


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_class(request):
    """
        Take in uuid. Delete exactly one class with the given uuid.
    """
    # Get class
    get_by_uuid(ClassMetadata, 'Class', request.POST.get('uuid')).delete()

    return Response({'details': 'Deleted'})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_class(request):
    """
        Take in uuid. 

        Return explicit info of that class (User info will be provided with name, mobile, email and uuid).
    """
    return Response(
        ClassMetadataSerializer(
            get_by_uuid(ClassMetadata, 'Class', request.GET.get('uuid'))
        ).data
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_class(request):
    """
        Take in student_uuid (optional). Param student_uuid represents uuid of a student. 

        If student_uuid is provided return all classes of the given student (No explicit info of students, just number of students).

        If none is provided return all classes in db with similar format of student_uuid.
    """
    classMeta = ClassMetadata.objects.all()

    # student_uuid is provided
    student_uuid = request.GET.get('student_uuid')
    if student_uuid is not None:
        # Get student by uuid
        student = get_by_uuid(
            CustomUser, 'Student', student_uuid)

        classMeta = student.student_classes.all()

    data = ClassMetadataSerializer(
        classMeta, many=True).exclude_field('students').data

    return Response(data)
