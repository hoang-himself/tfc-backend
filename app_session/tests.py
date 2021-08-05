from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import (APIClient, APITestCase)

from master_api.utils import (
    prettyPrint, compare_dict,
    convert_time, prettyStr
)
from master_api.views import (
    CREATE_RESPONSE, EDIT_RESPONSE, GET_RESPONSE,
    DELETE_RESPONSE, LIST_RESPONSE
)
from master_db.models import (Schedule, Session)

from app_schedule.tests import create_sched
from app_class.tests import create_special_student


CustomUser = get_user_model()
NUM_SESSION = 10


def create_session(desc=0, sched=None):
    sched = sched if sched is not None else create_sched(desc)
    student = sched.classroom.students.all()
    if desc < len(student):
        student = student[desc]
    else:
        student = student.first()
    return Session.objects.create(
        schedule=sched,
        student=student,
        desc=f'Description {desc}',
        homework=desc,
        status=desc % 2
    )


class SessionTest(APITestCase):
    url = '/api/v1/session/'

    def setUp(self):
        self.sched = create_sched()

        self.sessions = []
        for i in range(NUM_SESSION):
            self.sessions.append(create_session(i, self.sched))

    def test_successful_created(self):
        client = APIClient()
        url = self.url + 'create'
        sched = create_sched(69)

        data = {
            'schedule': str(sched.uuid),
            'student': str(sched.classroom.students.all().first().uuid),
            'desc': 'Newly created',
            'homework': 69,
            'status': False
        }

        response = client.post(url, data)
        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED, msg=prettyStr(response.data))

        self.test_list(False, NUM_SESSION + 1)

    def test_successful_deleted(self):
        client = APIClient()
        url = self.url + 'delete'

        # Check response
        delete_uuid = self.sessions[0].uuid
        response = client.delete(url, data={'uuid': delete_uuid})
        self.assertEqual(response.status_code,
                         DELETE_RESPONSE['status'], msg=prettyStr(response.data))
        self.assertEqual(response.data, 'Deleted')

        # Check in db through list
        response = self.test_list(False, NUM_SESSION - 1)

        # Check if uuid still exists in db
        self.assertFalse(
            any([res['uuid'] == delete_uuid for res in response.data]))

    def test_successful_editted(self):
        client = APIClient()

        edit_uuid = str(self.sessions[0].uuid)
        data = {
            'uuid': edit_uuid,
            'desc': 'Description modified',
            'status': True,
            'homework': 19
        }

        response = client.patch(self.url + 'edit', data=data)

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
        get_uuid = str(self.sessions[0].uuid)

        response = client.get(url, {'uuid': get_uuid})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], get_uuid)

    def test_list(self, printOut=True, length=None):
        client = APIClient()
        url = self.url + 'reverse'
        length = length if length is not None else NUM_SESSION

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), length)

        if printOut:
            print("\n ============List All DB Visualizing============")
            prettyPrint(response.data)
            print("\n ============List All DB Visualizing============")
        else:
            return response
