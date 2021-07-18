from django.http import response
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from master_db.models import Course
from master_api.utils import prettyPrint


# Create your tests here.
NUM_COURSE = 10

class CourseTest(TestCase):
    url = '/api/v1/course/'

    def setUp(self):
        self.courses = []
        for i in range(NUM_COURSE):
            course = Course(
                name=f'Anonymous {i}',
                duration=i,
                desc=f'Iteration {i}'
            )
            course.save()
            course.tags.add(
                *[('even ' if x % 2 == 0 else 'odd ') + str(x) for x in range(i + 1)])
            self.courses.append(course)

    def compare_dict(self, dict1, dict2):
        for key, value in dict1.items():
            if isinstance(value, list):
                value = set(value)
                dict2[key] = set(dict2[key])
            self.assertTrue(
                value == dict2[key], msg=f"{key}: {value} <-> {dict2[key]} => {value == dict2[key]}")

    def test_successful_created(self):
        client = APIClient()

        data = {
            'name': 'some name',
            'tags': '1, 2, 3, 4, 5, 6, 7',
            'duration': 69,
            'desc': 'some description'
        }
        response = client.post(self.url + 'create', data=data)

        self.assertEqual(response.data, {'detail': 'Ok'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check in db through list
        response = self.test_list(False, NUM_COURSE + 1)

        # Check for matched in db
        found = False
        for res in response.data:
            if res['name'] == data['name']:
                found = True
                res = dict(res)
                res.pop('uuid')
                data['tags'] = data['tags'].replace(' ', '').split(',')
                self.compare_dict(data, res)
                break
        self.assertTrue(found, msg="Not found in db")

    def test_successful_editted(self):
        client = APIClient()

        edit_uuid = str(self.courses[0].uuid)
        data = {
            'uuid': edit_uuid,
            'name': 'Name modified',
            'tags': 'this, has, been, changed',
            'desc': 'This description has been changed',
            'duration': 69
        }

        response = client.post(self.url + 'edit', data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check in db through list
        response = self.test_list(False)

        # Check if course in db has been changed
        found = False
        for res in response.data:
            if res['uuid'] == edit_uuid:
                # Indicate found, change formdata to python objects
                found = True
                data.pop('uuid')
                data['tags'] = data['tags'].replace(' ', '').split(',')
                # Check every element
                self.compare_dict(data, res)
                break
        # Check if found the editted
        self.assertTrue(found, msg="Not found in db")

    def test_successful_deleted(self):
        client = APIClient()

        # Check response
        delete_uuid = self.courses[0].uuid
        response = client.post(self.url + 'delete', data={'uuid': delete_uuid})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'detail': 'Deleted'})

        # Check in db through list
        response = self.test_list(False, NUM_COURSE - 1)

        # Check if uuid still exists in db
        for res in response.data:
            self.assertFalse(res.get('uuid') == delete_uuid)

    def test_successful_get(self):
        client = APIClient()
        url = self.url + 'get'
        get_uuid = str(self.courses[0].uuid)

        response = client.get(url, data={'uuid': get_uuid})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], get_uuid)

    def test_list(self, printOut=True, length=None):
        client = APIClient()
        length = length if length is not None else NUM_COURSE

        response = client.get(self.url + 'list')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), length)

        if printOut:
            print("\n ------------List Visualizing------------")
            prettyPrint(response.data)
            print("\n ------------List Visualizing------------")

        return response

    def test_get_tags(self):
        client = APIClient()
        url = self.url + 'get-tags'
        limit = 5

        def check_tags(data):
            i = 0
            for res in data:
                index = int(res['name'][-1])
                num = res['num_times']
                self.assertTrue(index == i and num == 10 - i,
                                msg=f"[get-tags] Iteration {i}: index: {index} and num: {num}")
                i += 1

        response = client.get(url)
        self.assertEqual(len(response.data), NUM_COURSE)
        check_tags(response.data)

        response = client.get(url, data={'limit': limit})
        self.assertEqual(len(response.data), limit)
        check_tags(response.data)

    def test_recommend_tags(self):
        client = APIClient()
        url = self.url + 'recommend-tags'

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
                self.assertTrue(index == i,
                                msg=f"[reccomend-tags] Iteration {i}: index: {index}")
                i += 2

        response = client.get(url, data={'txt': 'ev'})
        check_even_odd(response.data, True)

        response = client.get(url, data={'txt': 'od'})
        check_even_odd(response.data, False)
