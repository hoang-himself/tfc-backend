from django.http import response
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from master_db.models import Course, ClassMetadata, Schedule
from master_api.utils import (prettyPrint, compare_dict,
                              convert_time, prettyStr)
from master_api.views import (CREATE_RESPONSE, EDIT_RESPONSE, GET_RESPONSE,
                              DELETE_RESPONSE, LIST_RESPONSE,)

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
            'classroom': self.klass.uuid,
            'time_start': '1969-06-09 15:30',
            'time_end': '1970-06-09 15:30',
            'desc': 'Newly created'
        }

        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.test_list(False, NUM_SCHED + 1)

    def test_successful_deleted(self):
        client = APIClient()
        url = self.url + 'delete'

        # Check response
        delete_uuid = self.scheds[0].uuid
        response = client.post(url, data={'uuid': delete_uuid})
        self.assertEqual(response.status_code,
                         DELETE_RESPONSE['status'], msg=prettyStr(response.data))
        self.assertEqual(response.data, 'Deleted')

        # Check in db through list
        response = self.test_list(False, NUM_SCHED - 1)

        # Check if uuid still exists in db
        self.assertFalse(
            any([res['uuid'] == delete_uuid for res in response.data]))

    def test_successful_editted(self):
        client = APIClient()
        klass = create_class(69)

        edit_uuid = str(self.scheds[0].uuid)
        data = {
            'uuid': edit_uuid,
            'classroom': str(klass.uuid),
            'time_start': '6069-06-19 19:36',
            'time_end': '9069-06-19 19:36',
            'desc': 'Description modified'
        }

        response = client.post(self.url + 'edit', data=data)

        self.assertEqual(response.status_code,
                         EDIT_RESPONSE['status'], msg=prettyStr(response.data))

        # Check in db through list
        response = self.test_list(False)

        # Check if course in db has been changed
        found = False
        for res in response.data:
            if res['uuid'] == edit_uuid:
                # Indicate found, change formdata to python objects
                found = True
                res['time_start'] = res['time_start'][:16].replace('T', ' ')
                res['time_end'] = res['time_end'][:16].replace('T', ' ')
                # Check every element
                compare_dict(self, data, res)
                self.assertTrue(res['created'] != res['modified'],
                                msg=f"\n ----created must not equal modified----\n - created: {res['created']} \n - modified: {res['modified']}")
                break
        # Check if found the editted
        self.assertTrue(found, msg="Not found in db")

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
