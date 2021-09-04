from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import (APIClient, APITestCase)

from app_class.tests import (create_class, create_special_student)
from master_api.utils import (
    prettyPrint, compare_dict, convert_time, prettyStr
)
from master_api.views import (
    CREATE_RESPONSE, EDIT_RESPONSE, GET_RESPONSE, DELETE_RESPONSE, LIST_RESPONSE
)
from master_db.models import Schedule

CustomUser = get_user_model()
NUM_STUDENT_EACH = 10
NUM_SCHED = 10


def create_sched(desc=0, classes=None):
    classes = classes if classes is not None else create_class(desc)
    return Schedule.objects.create(
        classroom=classes,
        time_start=convert_time(f'20{desc:02d}-06-09 15:09'),
        time_end=convert_time(f'20{desc:02d}-06-09 17:09'),
        desc=f'Description {desc}'
    )


class ScheduleTest(APITestCase):
    url = reverse('app_schedule:schedule_mgmt')
    client = APIClient()

    def setUp(self):
        self.classes = [create_class(0), create_class(1)]

        self.scheds = []
        for i in range(NUM_SCHED):
            self.scheds.append(create_sched(i, self.classes[i % 2]))

        # Create user to generate header
        CustomUser.objects.create_user(
            email='user1@tfc.com',
            password='iamuser1',
            first_name='First',
            last_name='Last',
            birth_date='2001-07-31',
            mobile='0123456789',
            male=True,
            address='My lovely home'
        )
        data = {'email': 'user1@tfc.com', 'password': 'iamuser1'}
        response = self.client.post(reverse('app_auth:login'), data=data)
        access_token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {access_token}')

    def test_successful_created(self):
        # Format: YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]
        data = {
            'classroom': self.classes[0].uuid,
            'time_start': '1969-06-09 15:30',
            'time_end': '1970-06-09 15:30',
            'desc': 'Newly created'
        }

        response = self.client.post(self.url, data)
        self.assertEqual(
            response.status_code,
            CREATE_RESPONSE['status'],
            msg=prettyStr(response.data)
        )

        self.test_list(False, NUM_SCHED + 1)

    def test_successful_deleted(self):
        # Check response
        delete_uuid = self.scheds[0].uuid
        response = self.client.delete(self.url, data={'uuid': delete_uuid})
        self.assertEqual(
            response.status_code,
            DELETE_RESPONSE['status'],
            msg=prettyStr(response.data)
        )
        self.assertEqual(response.data, 'Deleted')

        # Check in db through list
        response = self.test_list(False, NUM_SCHED - 1)

        # Check if uuid still exists in db
        self.assertFalse(
            any([res['uuid'] == delete_uuid for res in response.data])
        )

    def test_successful_editted(self):
        classes = create_class(69)

        edit_uuid = str(self.scheds[0].uuid)
        data = {
            'uuid': edit_uuid,
            'classroom': str(classes.uuid),
            'time_start': '6069-06-19 19:36',
            'time_end': '9069-06-19 19:36',
            'desc': 'Description modified'
        }

        response = self.client.patch(self.url, data=data)

        self.assertEqual(
            response.status_code,
            EDIT_RESPONSE['status'],
            msg=prettyStr(response.data)
        )

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
                self.assertTrue(
                    res['created'] != res['modified'],
                    msg=
                    f"\n ----created must not equal modified----\n - created: {res['created']} \n - modified: {res['modified']}"
                )
                break
        # Check if found the editted
        self.assertTrue(found, msg="Not found in db")

    def test_successful_get(self):
        get_uuid = str(self.scheds[0].uuid)

        response = self.client.get(self.url, data={'uuid': get_uuid})
        self.assertEqual(
            response.status_code,
            GET_RESPONSE['status'],
            msg=prettyStr(response.data)
        )
        self.assertEqual(response.data['uuid'], get_uuid)

    def test_list(self, printOut=True, length=None):
        url = reverse('app_schedule:reverse')
        length = length if length is not None else NUM_SCHED

        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            LIST_RESPONSE['status'],
            msg=prettyStr(response.data)
        )
        self.assertEqual(len(response.data), length)

        if printOut:
            print("\n ============List All DB Visualizing============")
            prettyPrint(response.data)
            print("\n ============List All DB Visualizing============")
        else:
            return response

        # Special case for listing schedules in a given class
        response = self.client.get(
            url, data={'class_uuid': self.classes[1].uuid}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), int(NUM_SCHED / 2))

        # Check for student presence in every schedule
        for d in response.data:
            self.assertEqual(d['classroom']['uuid'], self.classes[1].uuid)
            self.assertTrue(
                int(d['desc'][-1]) % 2 == 1, msg=f"Desc should be odd"
            )

        print("\n ============List Class's Visualizing============")
        prettyPrint(response.data)
        print("\n ============List Class's Visualizing============")
        print(
            f"Note: All schedule's description NO. should be odd from 0 to {NUM_SCHED - 1}"
        )

        # Special case for listing student participates in many schedules
        std = create_special_student()

        for s in self.scheds:
            if int(s.classroom.name[-1]) % 3 == 0:
                s.classroom.students.add(std)

        student_uuid = std.uuid
        response = self.client.get(url, data={'student_uuid': student_uuid})

        # Check for student presence in every schedule
        for d in response.data:
            for s in self.scheds:
                if s.classroom.uuid == d['uuid']:
                    self.assertTrue(
                        int(d['desc'][-1]) % 3 == 0,
                        msg=f"Desc should be divisible by 3"
                    )
                    self.assertTrue(
                        any(
                            [
                                student_uuid == std.uuid
                                for std in s.classroom.students.all()
                            ]
                        ),
                        msg=f"Student with uuid {student_uuid}"
                        f"does not exist in class with uuid {s.classroom.uuid}"
                    )
                    break

        print("\n ============List Student's Visualizing============")
        prettyPrint(response.data)
        print("\n ============List Student's Visualizing============")
        print(
            f"Note: All schedule's description NO. should be divisible by 3 in range from 0 to {NUM_SCHED - 1}"
        )
