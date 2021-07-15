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
        for i in range(10):
            Course.objects.create(
                name=f'Anonymous {i}',
                tags=range(i + 1),
                duration=i * 10,
                desc=f'Iteration {i}'
            )

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

    def test_list(self):
        client = APIClient()

        response = client.get(self.url + 'list')
        print(response.data)
