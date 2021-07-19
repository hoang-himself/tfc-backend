from django.http import response
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from master_db.models import Course, ClassMetadata, Schedule
from master_api.utils import prettyPrint, compare_dict, convert_time

from app_class.tests import create_class


CustomUser = get_user_model()
NUM_STUDENT_EACH = 10
NUM_SCHED = 10


class ScheduleTest(TestCase):
    url = '/api/v1/schedule/'

    def setUp(self):
        self.klass = create_class()

        self.scheds = []
        for i in range(NUM_SCHED):
            sched = Schedule(
                classroom=self.klass,
                time_start=convert_time(f'20{i:02d}-06-09 16:09'),
                time_end=convert_time(f'30{i:02d}-06-09 16:09'),
                desc=f'Description {i}'
            )
            sched.save()
            self.scheds.append(sched)

    def test_successful_created(self):
        client = APIClient()
        url = self.url + 'create'

        # Format: YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]
        data = {
            'class_uuid': self.klass.uuid,
            'time_start': '1969-06-09 15:30',
            'time_end': '1970-06-09 15:30',
            'desc': 'Newly created'
        }

        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_successful_get(self):
        client = APIClient()
        url = self.url + 'get'
        get_uuid = str(self.scheds[0].uuid)

        response = client.get(url, data={'uuid': get_uuid})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], get_uuid)

    def test_list(self, printOut=True, length=None):
        client = APIClient()
        url = self.url + 'list'
        length = length if length is not None else NUM_SCHED

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), length)

        if printOut:
            print("\n ------------List All DB Visualizing------------")
            prettyPrint(response.data)
            print("\n ------------List All DB Visualizing------------")
        else:
            return response
