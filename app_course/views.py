from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_protect

from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from master_db.models import Course
from master_db.serializers import CourseSerializer
from master_api.utils import get_by_uuid, formdata_bool
from master_api.views import create_object, edit_object, get_object, delete_object

import datetime

CustomUser = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def get_course(request):
    return get_object(Course, data=request.GET)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def create_course(request):
    return create_object(Course, data=request.data)


@api_view(['PATCH'])
@permission_classes([AllowAny])
@csrf_protect
def edit_course(request):
    return edit_object(Course, data=request.data)


@api_view(['DELETE'])
@permission_classes([AllowAny])
@csrf_protect
def delete_course(request):
    return delete_object(Course, data=request.data)


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
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

    return Response(tags)


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
def recommend_tags(request):
    """
        Take in txt.

        Return all tags containing txt as substring. If txt is empty return empty list.
    """
    txt = request.GET.get('txt')
    if txt is None or txt == '':
        return Response()

    tag_names = Course.tags.filter(
        name__contains=txt).values_list('name', flat=True)

    return Response(tag_names)


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_protect
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

    return Response(CourseSerializer(course, many=True).data)
