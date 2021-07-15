from django.http import response
from django.test import TestCase
from django.urls import reverse, get_urlconf
from rest_framework import status
from rest_framework.test import APIClient

from master_db.models import Course

import random
import string

# Create your tests here.


class CourseTest(TestCase):
    url = '/api/v1/course/'

    def setUp(self):
        self.courses = []
        for i in range(10):
            course = Course(
                name=f'Anonymous {i}',
                duration=i * 10,
                desc=f'Iteration {i}'
            )
            course.save()
            course.tags.add(*[str(x) for x in range(i + 1)])
            self.courses.append(course)

    def test_successful_created(self):
        client = APIClient()

        data = {
            'name': 'some name',
            'tags': '1, 2, 3, 4, 5, 6, 7',
            'duration': 69,
        }
        response = client.post(self.url + 'create', data)

        self.assertEqual(response.data, {'detail': 'Ok'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_successful_deleted(self):
        client = APIClient()

        # Check response
        delete_uuid = self.courses[0].uuid
        response = client.post(self.url + 'delete', data={'uuid': delete_uuid})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'detail': 'Deleted'})

        # Check in db through list
        response = client.get(self.url + 'list')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.courses) - 1)

        # Check if uuid still exists in db
        for res in response.data:
            self.assertFalse(res.get('uuid') == delete_uuid)

    def test_list(self):
        client = APIClient()

        response = client.get(self.url + 'list')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.courses))
