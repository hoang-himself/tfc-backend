from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_protect

from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from master_db.models import Course
from master_db.serializers import CourseSerializer
from master_api.utils import get_by_uuid, model_full_clean, edit_object, formdata_bool

import datetime

CustomUser = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def get_course(request):
    # TODO
    pass


@api_view(['POST'])
@permission_classes([AllowAny])
def create_course(request):
    """
        Take in name, desc, tags and duration

        Param tags must be in the form of: tag1, tag2, tag3 (whitespace is optional)
    """

    # Get fields. Should not use **request.POST because it will cause everything to be string -> invalid type
    course = Course(
        name=request.POST.get('name'),
        desc=request.POST.get('desc'),
        duration=request.POST.get('duration'),
    )

    # Validate model
    model_full_clean(course)

    # Save and update tags (Tags must be done this way to be saved in the database)
    course.save()
    course.tags.add(*request.POST.get('tags').replace(' ', '').split(','))

    return Response(
        data={
            'detail': 'Ok',
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def edit_course(request):
    """
        Take in uuid, name (optional), desc (optional), short_desc (optional), tags (optional) and duration (optional). Param uuid is the uuid of the course that needs editing, the other params are the fields that needs changing

        The optional params if not provided will not be updated. If the content provided is the same as the source, no change will be made.

        Param tags must be in the form of: tag1, tag2, tag3 (whitespace is optional)
    """

    modifiedDict = request.POST.copy()
    modifiedDict.pop('updated_at', None)
    modifiedDict.pop('created_at', None)

    # Get course
    course = get_by_uuid(
        Course, 'Course', modifiedDict.get('uuid'))

    # Update model: Set attributes and update updated_at
    if modifiedDict.get('duration') is not None:
        modifiedDict['duration'] = int(modifiedDict['duration'])

    modifiedList = edit_object(course, modifiedDict, ['tags'])

    if not modifiedList:
        return Response(data={'detail': 'modified nothing'}, status=status.HTTP_304_NOT_MODIFIED)
    else:
        modifiedList.append('modified')

    # Validate model
    model_full_clean(course)

    # Save and update tags (Tags must be done this way to be saved in the database)
    if not modifiedDict.get('tags') is None:
        modifiedList.append('tags')
        course.tags.clear()
        course.tags.add(*modifiedDict['tags'].replace(' ', '').split(','))

    course.save()

    return Response(
        data={
            'modified': modifiedList,
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_course(request):
    """
        Take in uuid. Delete the course with the given uuid.
    """
    # Get course
    course = get_by_uuid(Course, 'Course', request.POST.get('uuid'))

    # Delete
    course.delete()

    return Response(data={'detail': 'Deleted'}, status=status.HTTP_200_OK)


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
        data=tags,
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
            data=None,
            status=status.HTTP_200_OK
        )

    tag_names = Course.tags.filter(
        name__contains=txt).values_list('name', flat=True)

    return Response(
        data=tag_names,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_course(request):
    """
        Take in tags (optional). 

        If tags is provided, return all courses contain the tags, else return all
    """
    tags = request.GET.get('tags')

    if tags is None:
        course = Course.objects.all()
    else:
        course = Course.objects.filter(
            tags__name=tags.replace(' ', '').split(','))

    return Response(
        data=CourseSerializer(course, many=True).data,
        status=status.HTTP_200_OK
    )
