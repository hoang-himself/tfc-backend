from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from app_auth.utils import has_perm
from master_db.models import Course
from master_db.serializers import CourseSerializer

import datetime

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def create_course(request):
    """
        Take in name, desc, short_desc, tags and duration

        Param tags must be in the form of: tag1, tag2, tag3 (whitespace is optional)
    """

    # Get fields. Should not use **request.POST because it will cause everything to be string -> invalid type
    now = datetime.datetime.now().timestamp()
    course = Course(
        name=request.POST.get('name'),
        desc=request.POST.get('desc'),
        short_desc=request.POST.get('short_desc'),
        duration=request.POST.get('duration'),
        created_at=now,
        updated_at=now
    )

    # Validate model
    try:
        course.full_clean()
    except ValidationError as message:
        return Response(
            data={
                'details': 'Error',
                'message': dict(message)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Save and update tags (Tags must be done this way to be saved in the database)
    course.save()
    course.tags.add(*request.POST.get('tags').replace(' ', '').split(','))

    return Response(
        data={
            'details': 'Ok',
            'data': CourseSerializer(course).data
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def edit_course(request):
    """
        Take in target_name, name (optional), desc (optional), short_desc (optional), tags (optional) and duration (optional). Param target_name is the name of the course that needs editing, the other params are the fields that needs changing

        The optional params if not provided will not be updated. If the content provided is the same as the source, no change will be made.

        Param tags must be in the form of: tag1, tag2, tag3 (whitespace is optional)
    """

    modifiedList = []

    # Check existence
    try:
        course = Course.objects.get(name=request.POST.get('target_name'))
    except Course.DoesNotExist:
        return Response(
            data={
                'details': 'Error',
                'message': 'Course does not exist'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update model: Set attributes and update updated_at
    data = request.POST.copy()

    for key, value in data.items():
        if hasattr(course, key) and value != getattr(course, key) and key != 'tags':
            setattr(course, key, value)
            modifiedList.append(key)

    # Validate model
    try:
        course.full_clean()
    except ValidationError as message:
        return Response(
            data={
                'details': 'Error',
                'message': dict(message)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Save and update tags (Tags must be done this way to be saved in the database)
    tags = request.POST.get('tags')
    if not tags is None:
        modifiedList.append('tags')
        course.tags.clear()
        course.tags.add(*tags.replace(' ', '').split(','))

    if bool(modifiedList):
        modifiedList.append('updated_at')
        course.updated_at = datetime.datetime.now().timestamp()

    course.save()

    return Response(
        data={
            'details': 'Ok',
            'modified': modifiedList,
            # ! For testing purposes only, should be removed
            'data': CourseSerializer(course).data
        },
        status=status.HTTP_202_ACCEPTED
    )


def formdata_bool(var):
    low = var.lower()
    if low == 'true':
        return True
    if low == 'false':
        return False
    return None


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_course(request):
    """
        There are 2 options.

        Option 1: delete by name. This will only delete 1 course with the corresponding name because name is unique

        Option 2: delete by tags. Param tags, many, exact must be specified. Param many and exact is boolean type (valid if after lowered it is 'true' or 'false'). Param many allows to delete multiple with the tags, exact allows to delete course with exact tags or not.

        Param tags must be in the form of: tag1, tag2, tag3 (whitespace is optional)
    """

    # Option 1: name is presence, delete 1 course by name
    name = request.POST.get('name')
    if not name is None:
        try:
            Course.objects.get(name=name).delete()
        except Course.DoesNotExist:
            return Response(
                data={
                    'details': 'Error',
                    'message': 'Course does not exist'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            data={'details': 'Ok'},
            status=status.HTTP_200_OK
        )

    # Option 2: name is not presence, all other params are mandatory
    tags = request.POST.get('tags')
    many = request.POST.get('many')
    exact = request.POST.get('exact')

    # Check for all param presence
    returnDict = {}
    if tags is None:
        returnDict.update({'tags': 'This field cannot be empty'})
    else:
        tags = tags.replace(' ', '').split(',')

    if many is None:
        returnDict.update({'many': 'This field cannot be empty'})
    else:
        many = formdata_bool(many)

    if exact is None:
        returnDict.update({'exact': 'This field cannot be empty'})
    else:
        exact = formdata_bool(exact)

    # Return if at least one is missing
    if bool(returnDict):
        return Response(
            data={
                'details': 'Error',
                'message': returnDict,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate boolean values
    if many is None or exact is None:
        return Response(
            data={
                'details': 'Error',
                'message': 'Boolean value should be True or False',
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get filter by exact tags or not
    if exact:
        filter_name = {'tags__name': tags}
    else:
        filter_name = {'tags__name__in': tags}

    # Filter by tags
    course = Course.objects.filter(**filter_name)
    if not course:
        return Response(
            data={
                'details': 'Ok',
                'message': 'Deleted nothing'
            },
            status=status.HTTP_204_NO_CONTENT
        )

    # Check if delete many or not
    if not many:
        course = course.first()
        names = course.name
    else:
        names = course.values_list('name', flat=True)

    # Delete
    course.delete()

    return Response(
        data={
            'details': 'Ok',
            'deleted_names': names
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_tags(request):
    """
        Take in limit (optional)

        Get all tags in db sorted in most frequently used. If limit is specified, only return 'limit' number of tags.
    """
    limit = request.GET.get('limit')
    if limit is None:
        tags = Course.tags.most_common().values('name', 'num_times')
    else:
        tags = Course.tags.most_common()[:int(
            limit)].values('name', 'num_times')

    return Response(
        data={
            'details': 'Ok',
            'names': tags
        },
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def recommend_tags(request):
    """
        Take in txt.

        Return all tags containing txt as substring. If txt is empty return empty list.
    """
    txt = request.GET.get('txt')
    if txt is None or txt == '':
        return Response(
            data=[],
            status=status.HTTP_200_OK
        )

    tag_names = Course.objects.all().values_list('tags__name', flat=True).distinct()
    returnList = []
    for name in tag_names:
        if txt in name:
            returnList.append(name)

    return Response(
        data=returnList,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_course(request):
    """
        Take in tags and exact. If there is no tags the result will be all courses in the database. 

        If exact is True result will be courses with the exact tags, else result will be all courses with at least one same tag.

        Param tags must be in the form of: tag1, tag2, tag3 (whitespace is optional)
    """
    tags = request.GET.get('tags')

    if tags is None:
        course = Course.objects.all()
    else:
        exact = bool(request.GET.get('exact'))
        tags = tags.replace(' ', '').split(',')
        if exact:
            filter_name = {'tags__name': tags}
        else:
            filter_name = {'tags__name__in': tags}
        course = Course.objects.filter(**filter_name).distinct()

    data = CourseSerializer(course, many=True).data

    return Response(
        data=data,
        status=status.HTTP_200_OK
    )
