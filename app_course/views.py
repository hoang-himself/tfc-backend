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
                'message': message
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
        Take in target_name, name, desc, short_desc, tags and duration. Param target_name is the name of the course that needs editing, the other params are the fields that needs changing
        
        Param tags must be in the form of: tag1, tag2, tag3 (whitespace is optional)
    """
    
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
    data['tags'] = data['tags'].replace(' ', '').split(',')
    data['updated_at'] = datetime.datetime.now().timestamp()
    
    for key, value in data.items():
        if hasattr(course, key):
            setattr(course, key, value)
    
    # Validate model
    try:
        course.full_clean()
    except ValidationError as message:
        return Response(
            data={
                'details': 'Error',
                'message': message
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Save
    course.save()
    
    return Response(
        data={
            'details': 'Ok',
            # ! For testing purposes only, should be removed
            'data': CourseSerializer(course).data    
        },
        status=status.HTTP_202_ACCEPTED
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def list_course(request):
    data = CourseSerializer(Course.objects.all(), many=True).data
    
    return Response(
        data=data,
        status=status.HTTP_200_OK
    )