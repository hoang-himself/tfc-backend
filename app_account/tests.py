from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.urls import reverse

from PIL import Image

from rest_framework import status
from rest_framework.test import (APIClient, APITestCase)

from app_course.tests import create_course
from master_db.models import Course, ClassMetadata, PHONE_REGEX
from master_api.utils import (
    prettyPrint, prettyStr, compare_dict
)
from master_api.views import (
    CREATE_RESPONSE, EDIT_RESPONSE, DELETE_RESPONSE,
    GET_RESPONSE, LIST_RESPONSE
)

import json
import rstr
import io


CustomUser = get_user_model()
NUM_USER = 10


class TestUser(APITestCase):
    url = '/api/v1/account/'
    client = APIClient()

    def setUp(self):
        self.users = CustomUser.objects.bulk_create(
            [CustomUser(
                email=f'user{i}@tfc.com', password=make_password('iamuser'),
                first_name=f'Number{i}', last_name='User',
                birth_date='2001-07-31', mobile=rstr.xeger(PHONE_REGEX),
                male=i % 2, address='My lovely home',
            ) for i in range(NUM_USER)]
        )

        url = reverse('app_auth:login')
        data = {
            'email': 'user0@tfc.com',
            'password': 'iamuser'
        }
        response = self.client.post(url, data=data)
        token = response.data.get('token', None).get('access', None)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')

    def generate_photo_file(self, color=(0, 155, 0)):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=color)
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_successful_created(self):
        url = self.url + 'create'

        data = {
            'email': 'someuser@tfc.com', 'password': 'somepassword',
            'first_name': 'First', 'last_name': 'Last',
            'birth_date': '2001-07-31', 'mobile': rstr.xeger(PHONE_REGEX),
            'male': True, 'address': 'My lovely home',
            'is_active': False,
            'avatar': self.generate_photo_file(),
            'date_joined': '2010-12-12',
            'last_login': '2010-12-12T13:27:57',
        }

        response = self.client.post(url, data)
        self.assertEqual(
            response.status_code, CREATE_RESPONSE['status'],
            msg=prettyStr(response.data)
        )
        self.assertEqual(response.data, CREATE_RESPONSE['data'])
        self.test_list(False, NUM_USER + 1)

    def test_list(self, printOut=True, length=None):
        length = length if length is not None else NUM_USER
        client = APIClient()
        url = self.url + 'list'

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), length)
        if printOut:
            prettyPrint(response.data)
        else:
            return response

    def test_editted(self):
        url = self.url + 'edit'
        edit_uuid = self.users[0].uuid

        data = {
            'uuid': edit_uuid,
            'old_password': 'iamuser',
            'password': 'newpassword'
        }

        response = self.client.patch(url, data)
        self.assertEqual(
            response.status_code, EDIT_RESPONSE['status'],
            msg=prettyStr(response.data)
        )

    def test_successful_deleted(self):
        url = self.url + 'delete'
        delete_uuid = self.users[0].uuid

        response = self.client.delete(url, {'uuid': delete_uuid})
        self.assertEqual(response.status_code, DELETE_RESPONSE['status'],
                         msg=prettyStr(response.data))
        self.assertEqual(response.data, DELETE_RESPONSE['data'])
        response = self.test_list(False, NUM_USER - 1)


# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse

# from freezegun import freeze_time

# from rest_framework import status
# from rest_framework.test import APIClient

# CustomUser = get_user_model()


# class GetSelfTests(TestCase):

#     @freeze_time("2016-12-21 16:00:00", tz_offset=+7)
#     def setUp(self):
#         CustomUser.objects.create_user(
#             email='user1@tfc.com', password='iamuser1',
#             first_name='First', last_name='Last',
#             birth_date='2001-07-31', mobile='0123456789',
#             male=True, address='My lovely home',
#         )

#     @freeze_time("2016-12-21 16:00:00", tz_offset=+7)
#     def test_no_filter(self):
#         url = reverse('app_account:get-self')
#         client = APIClient()
#         data = {
#             'email': 'user1@tfc.com',
#             'password': 'iamuser1'
#         }
#         response = client.post(reverse('app_auth:login'), data=data)
#         response = client.get(url)
#         serializer = {
#             'email': 'user1@tfc.com', 'first_name': 'First',
#             'last_name': 'Last', 'birth_date': '2001-07-31',
#             'mobile': '0123456789', 'male': True, 'address': 'My lovely home',
#         }

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertTrue(serializer.items() <= response.data.items())

#     @freeze_time("2016-12-21 16:00:00", tz_offset=+7)
#     def test_fragmented_filter(self):
#         url = '{}?{}'.format(reverse('app_account:get-self'), '&'.join(
#             [
#                 'filter=email',
#                 'filter=mobile',
#                 'filter=birth_date',
#             ]  # /api/v1/account/get?filter=email&filter=mobile&filter=birth_date
#         ))
#         client = APIClient()
#         data = {
#             'email': 'user1@tfc.com',
#             'password': 'iamuser1'
#         }
#         response = client.post(reverse('app_auth:login'), data=data)
#         response = client.get(url)
#         serializer = {
#             'email': 'user1@tfc.com',
#             'mobile': '0123456789',
#             'birth_date': '2001-07-31',
#         }

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(serializer, response.data)


# class ListUserTests(TestCase):
#     url = reverse('app_account:list-user')

#     # TODO


# class CreateUserTests(TestCase):
#     url = reverse('app_account:create-user')

#     # TODO


# class EditUserTests(TestCase):
#     url = reverse('app_account:edit-user')

#     # TODO


# class DeleteUserTests(TestCase):
#     url = reverse('app_account:delete-user')

#     # TODO


# class ListStaffTests(TestCase):
#     url = reverse('app_account:list-staff')

#     # TODO


# class CreateStaffTests(TestCase):
#     url = reverse('app_account:create-staff')

#     # TODO


# class EditStaffTests(TestCase):
#     url = reverse('app_account:edit-staff')

#     # TODO


# class DeleteStaffTests(TestCase):
#     url = reverse('app_account:delete-staff')

#     # TODO
