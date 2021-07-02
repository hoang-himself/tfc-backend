from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes


from app_auth.utils import has_perm
from master_db.models import MyUser, ClassMetadata, Course
from master_db.serializers import ClassMetadataSerializer

import re
import datetime
import json
import jwt

def verify_teacher(user):
    # In production
    return user.mobile == '0919877216'

@api_view(['POST'])
@permission_classes([AllowAny])
def create_class(request):
    """
        Take in course_name, name, teacher_uuid (Optional), status (Need revision), std_uuids (Optional)

        Param std_uuids must be in form of: uuid1, uuid2, uuid3 (whitespace is optional)
    """
    std_uuids = request.POST.get('std_uuids')
    teacher = request.POST.get('teacher_uuid')

    # Get course corresponding to course_name
    try:
        course = Course.objects.get(name=request.POST.get('course_name'))
    except Course.DoesNotExist:
        return Response(
            data={
                'details': 'Error',
                'message': 'Course does not exist'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Get teacher if available
    if teacher is not None:
        try:
            teacher = MyUser.objects.get(uuid=teacher)
        except (MyUser.DoesNotExist, ValidationError) as e:
            if type(e).__name__ == 'DoesNotExist':
                message = 'Teacher user does not exist'
                stat = status.HTTP_404_NOT_FOUND
            else:
                message = dict(e)
                stat = status.HTTP_400_BAD_REQUEST
            return Response(
                data={
                    'details': 'Error',
                    'message': message
                },
                status=stat
            )
        
        if not verify_teacher(teacher):
            return Response(
                data={
                    'details': 'Error',
                    'message': 'User is not a teacher'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    # Construct model
    now = datetime.datetime.now().timestamp()
    classMeta = ClassMetadata(
        course=course,
        name=request.POST.get('name'),
        teacher=teacher,
        status=request.POST.get('status'),
        created_at=now,
        updated_at=now
    )

    # Validate model
    try:
        classMeta.full_clean()
    except ValidationError as message:
        print(message)
        return Response(
            data={
                'details': 'Error',
                'message': dict(message)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get students from std_uuids
    uuids = None
    if not std_uuids is None:
        # Handling UUID validation
        try:
            db = MyUser.objects.filter(
                uuid__in=std_uuids.replace(' ', '').split(','))
        except ValidationError as message:
            return Response(
                data={
                    'details': 'Error',
                    'message': dict(message)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Store students id for adding
        students = db.values_list('pk', flat=True)
        # Store uuids for visualizing added students, if one does not show up it is not found
        uuids = db.values_list('uuid', flat=True)

    # Save and add students (M2M field must be added this way to save)
    classMeta.save()
    if not std_uuids is None:
        classMeta.students.add(*students)

    return Response(
        data={
            'details': 'Ok',
            'teacher_added': not teacher is None,
            'students_added': uuids
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def add_student(request):
    """
        Take in name, uuids. Param name represents class name and uuids is a list of student's uuid

        Param uuids must be in the form of: uuid1, uuid2, uuid3 (whitespace is optional)
    """
    std_uuids = request.POST.get('uuids')

    # Get class
    try:
        classMeta = ClassMetadata.objects.get(name=request.POST.get('name'))
    except ClassMetadata.DoesNotExist:
        return Response(
            data={
                'details': 'Error',
                'message': 'Class does not exist'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Get all students with uuids
    uuids = None
    if not std_uuids is None:
        std_uuids = std_uuids.replace(' ', '').split(',')
        # Handling UUID validation
        try:
            db = MyUser.objects.filter(uuid__in=std_uuids)
        except ValidationError as message:
            return Response(
                data={
                    'details': 'Error',
                    'message': dict(message)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Store students id for adding
        students = db.values_list('pk', flat=True)
        # Store uuids for visualizing added students, if one does not show up it is not found
        uuids = db.values_list('uuid', flat=True)

    # Add students
    classMeta.students.add(*students)

    return Response(
        data={
            'details': 'Ok',
            'students_added': uuids
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_student(request):
    """
        Take in name and uuids. Param name represents class name, uuids is a list of student uuid.

        Every uuid must be a valid student or else removal will not be performed.

        Param uuids must be in the form of: uuid1, uuid2, uuid3 (whitespace is optional)
    """
    std_uuids = request.POST.get('uuids')

    # Get class
    try:
        classMeta = ClassMetadata.objects.get(name=request.POST.get('name'))
    except ClassMetadata.DoesNotExist:
        return Response(
            data={
                'details': 'Error',
                'message': 'Class does not exist'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Get students uuids
    uuids = None
    if not std_uuids is None:
        std_uuids = std_uuids.replace(' ', '').split(',')
        # Handling UUID validation
        try:
            students = classMeta.students.filter(uuid__in=std_uuids)
        except ValidationError as message:
            return Response(
                data={
                    'details': 'Error',
                    'message': dict(message)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # Store uuids for visualizing added students, if one does not show up it is not found
        uuids = [str(o)
                 for o in students.values_list('uuid', flat=True).filter()]

        if len(uuids) != len(std_uuids):
            return Response(
                data={
                    'details': 'Error',
                    # Average: O(N), Worst: O(N^2)
                    'not_found': set(std_uuids).difference(set(uuids))
                }
            )

    # Remove students from class if all uuids are present
    classMeta.students.remove(*students.values_list('pk', flat=True))

    return Response(
        data={
            'details': 'Ok',
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def edit_class(request):
    """
        Take in target_name, course_name (optional), teacher (optional), course (optional), name (optional), status (optional).

        The optional params if not provided will not be updated. If the content provided is the same as the source, no change will be made.

        If at least one optional param is provided, updated_at will be updated
    """
    teacher = request.POST.get('teacher_uuid')
    course = request.POST.get('course_name')
    name = request.POST.get('name')
    stat = request.POST.get('status')

    # List represents modified fields
    modifiedList = []

    # Get class
    try:
        classMeta = ClassMetadata.objects.get(
            name=request.POST.get('target_name'))
    except ClassMetadata.DoesNotExist:
        return Response(
            data={
                'details': 'Error',
                'message': 'Class does not exist'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Get teacher if provided
    if not teacher is None:
        try:
            teacher = MyUser.objects.get(uuid=teacher)
        except (MyUser.DoesNotExist, ValidationError) as e:
            if type(e).__name__ == 'DoesNotExist':
                message = 'Teacher user does not exist'
            else:
                message = dict(e)
            return Response(
                data={
                    'details': 'Error',
                    'message': message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not verify_teacher(teacher):
            return Response(
                data={
                    'details': 'Error',
                    'message': 'User is not a teacher'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    # Get course if provided
    if not course is None:
        try:
            course = Course.objects.get(name=course)
        except Course.DoesNotExist:
            return Response(
                data={
                    'details': 'Error',
                    'message': 'Course does not exist'
                },
                status=status.HTTP_404_NOT_FOUND
            )

    # Update the provided fields if content changed
    if not name is None and name != classMeta.name:
        classMeta.name = name
        modifiedList.append('name')
    if not course is None and course != classMeta.course:
        classMeta.course = course
        modifiedList.append('course')
    if not teacher is None and teacher != classMeta.teacher:
        classMeta.teacher = teacher
        modifiedList.append('teacher')
    if not stat is None and stat != classMeta.status:
        classMeta.status = stat
        modifiedList.append('status')
    if bool(modifiedList):
        classMeta.updated_at = datetime.datetime.now().timestamp()
        modifiedList.append('updated_at')

    # Validate model
    try:
        classMeta.full_clean()
    except ValidationError as message:
        return Response(
            data={
                'details': 'Error',
                'message': dict(message)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Save
    classMeta.save()

    return Response(
        data={
            'details': 'Ok',
            'modified': modifiedList,
            # ! For testing purposes only, should be removed
            'data': ClassMetadataSerializer(classMeta).data
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_class(request):
    """
        Take in name. Delete exactly one class with the given name.
    """
    # Get class
    try:
        classMeta = ClassMetadata.objects.get(name=request.POST.get('name'))
    except ClassMetadata.DoesNotExist:
        return Response(
            data={
                'details': 'Error',
                'message': 'Class does not exist'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    # Delete
    classMeta.delete()

    return Response(
        data={
            'details': 'Ok',
            # ! For testing purposes only, should be removed
            'data' : ClassMetadataSerializer(classMeta).data,
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_class(request):
    return Response(
        data=ClassMetadataSerializer(
            ClassMetadata.objects.all(), many=True).data
    )
