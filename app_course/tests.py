from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import (APIClient, APITestCase)

from master_api.utils import (prettyPrint, compare_dict)
from master_api.views import (
    CREATE_RESPONSE, EDIT_RESPONSE, DELETE_RESPONSE, GET_RESPONSE, LIST_RESPONSE
)
from master_db.models import Course

import json

CustomUser = get_user_model()
NUM_COURSE = 10


def create_course(desc=0, tags=None):
    course = Course(
        name=f'Course-{desc}',
        duration=desc if type(desc) == int else 69,
        desc=f'Course-{desc} description'
    )
    course.save()
    tags = tags if tags is not None else ['dummy', 'course', f'at-{desc}']
    course.tags.add(*tags)

    return course


class CourseTest(APITestCase):
    url = reverse('app_course:course_mgmt')
    client = APIClient()

    def setUp(self):
        self.courses = []
        for i in range(NUM_COURSE):
            self.courses.append(
                create_course(
                    i, [
                        ('even ' if x % 2 == 0 else 'odd ') + str(x)
                        for x in range(i + 1)
                    ]
                )
            )

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
        data = {
            'name': 'some name',
            'tags': '["1", "2", "3", "4", "5", "6", "7"]',
            'duration': 69,
            'desc': 'some description',
        }
        response = self.client.post(self.url, data=data)

        self.assertEqual(response.data, 'Ok')
        self.assertEqual(
            response.status_code,
            CREATE_RESPONSE['status'],
            msg=f"{response.data}"
        )

        # Check in db through list
        response = self.test_list(False, NUM_COURSE + 1)

        # Check for matched in db
        found = False
        for res in response.data:
            if res['name'] == data['name']:
                found = True
                res = dict(res)
                data['tags'] = json.loads(data['tags'])
                compare_dict(self, data, res)
                break
        self.assertTrue(found, msg="Not found in db")

    def test_successful_editted(self):
        edit_uuid = str(self.courses[0].uuid)
        data = {
            'uuid': edit_uuid,
            'tags': '["this", "has", "been", "changed"]',
            'desc': 'This description has been changed',
            'duration': 69,
        }

        response = self.client.patch(self.url, data=data)

        self.assertEqual(
            response.status_code,
            EDIT_RESPONSE['status'],
            msg=str(response.data)
        )

        # Check in db through list
        response = self.test_list(False)

        # Check if course in db has been changed
        found = False
        for res in response.data:
            if res['uuid'] == edit_uuid:
                # Indicate found, change formdata to python objects
                found = True
                data['tags'] = json.loads(data['tags'])
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

    def test_successful_deleted(self):
        # Check response
        delete_uuid = self.courses[0].uuid
        response = self.client.delete(self.url, data={'uuid': delete_uuid})
        self.assertEqual(
            response.status_code,
            DELETE_RESPONSE['status'],
            msg=f"{response.data}"
        )
        self.assertEqual(response.data, 'Deleted')

        # Check in db through list
        response = self.test_list(False, NUM_COURSE - 1)

        # Check if uuid still exists in db
        self.assertFalse(
            any([res['uuid'] == delete_uuid for res in response.data])
        )

    def test_successful_get(self):
        get_uuid = str(self.courses[0].uuid)

        response = self.client.get(self.url, data={'uuid': get_uuid})

        self.assertEqual(
            response.status_code,
            GET_RESPONSE['status'],
            msg=f"{response.data}"
        )
        self.assertEqual(response.data['uuid'], get_uuid)

    def test_list(self, printOut=True, length=None):
        url = reverse('app_course:reverse')
        length = length if length is not None else NUM_COURSE

        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            LIST_RESPONSE['status'],
            msg=f"{response.data}"
        )
        self.assertEqual(len(response.data), length)

        if printOut:
            print("\n ============List Visualizing============")
            prettyPrint(response.data)
            print("\n ============List Visualizing============")

        return response

    def test_get_tags(self):
        url = reverse('app_course:get_tag')
        limit = 5

        def check_tags(data):
            i = 0
            for res in data:
                index = int(res['name'][-1])
                num = res['num_times']
                self.assertTrue(
                    index == i and num == 10 - i,
                    msg=f"[tag/get] Iteration {i}: index: {index} and num: {num}"
                )
                i += 1

        response = self.client.get(url)
        self.assertEqual(len(response.data), NUM_COURSE)
        check_tags(response.data)

        response = self.client.get(url, data={'limit': limit})
        self.assertEqual(len(response.data), limit)
        check_tags(response.data)

    def test_recommend_tags(self):
        url = reverse('app_course:find_tag')

        def check_even_odd(data, even):
            prefix = 'even' if even else 'odd'
            l = NUM_COURSE
            # Number of evens = total / 2 + total % 2, number of odds = total / 2
            self.assertEqual(len(data), int(l / 2) + (l % 2 if even else 0))
            i = int(not even)
            for res in data:
                index = int(res[-1])
                pre = res[:-2]
                self.assertEqual(pre, prefix, msg="Prefix not matched")
                self.assertTrue(
                    index == i,
                    msg=f"[reccomend-tags] Iteration {i}: index: {index}"
                )
                i += 2

        response = self.client.get(url, data={'txt': 'ev'})
        check_even_odd(response.data, True)

        response = self.client.get(url, data={'txt': 'od'})
        check_even_odd(response.data, False)
