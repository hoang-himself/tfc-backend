from django.contrib.auth import get_user_model

from rest_framework import (exceptions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from master_db.models import Course
from master_db.serializers import CourseSerializer
from master_api.views import (
    create_object, edit_object, get_object, delete_object
)

CustomUser = get_user_model()


class CourseView(APIView):
    def post(self, request):
        return create_object(Course, data=request.data)

    def get(self, request):
        return get_object(Course, data=request.GET)

    def patch(self, request):
        return edit_object(Course, data=request.data)

    def delete(self, request):
        return delete_object(Course, data=request.data)


class TagView(APIView):
    def get(self, request):
        """
            Take in limit (optional)

            Get all tags in db sorted in most frequently used. If limit is specified, only return 'limit' number of tags.
        """
        limit = request.GET.get('limit')
        if limit is None:
            tags = Course.tags.most_common().values('name', 'num_times')
        else:
            tags = Course.tags.most_common()[:int(limit)].values(
                'name', 'num_times'
            )

        return Response(tags)


class FindTagView(APIView):
    def get(self, request):
        """
            Take in txt.

            Return all tags containing txt as substring. If txt is empty return empty list.
        """
        txt = request.GET.get('txt')
        if txt is None or txt == '':
            return Response()

        tag_names = Course.tags.filter(name__contains=txt).values_list('name', flat=True)

        return Response(tag_names)


class FindCourseView(APIView):
    def get(self, request):
        """
            Take in tags (optional).

            If tags is provided, return all courses contain the tags, else return all
        """
        tags = request.GET.get('tags')

        if tags is None:
            course = Course.objects.all()
        else:
            course = Course.objects.filter(
                tags__name=tags.replace(' ', '').split(',')
            )

        # student_uuid is provided
        student_uuid = request.GET.get('student_uuid')
        if student_uuid is not None:
            course = Course.objects.filter()

        return Response(CourseSerializer(course, many=True).data)
