from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.urls import reverse

from PIL import Image

from rest_framework.test import (APIClient, APITestCase)

from master_api.utils import (prettyPrint, prettyStr)
from master_api.views import (
    CREATE_RESPONSE, EDIT_RESPONSE, DELETE_RESPONSE, GET_RESPONSE, LIST_RESPONSE
)
from master_db.models import PHONE_REGEX

import rstr
import io

CustomUser = get_user_model()
NUM_USER = 10
GENDERS = ['M','F','O']


class TestUser(APITestCase):
    url = reverse('app_account:user_mgmt')
    client = APIClient()

    def setUp(self):
        self.users = CustomUser.objects.bulk_create(
            [
                CustomUser(
                    email=f'user{i}@tfc.com',
                    password=make_password('iamuser'),
                    first_name=f'Number{i}',
                    last_name='User',
                    birth_date='2001-07-31',
                    mobile=rstr.xeger(PHONE_REGEX),
                    male=i % 2,
                    address='My lovely home',
                ) for i in range(NUM_USER)
            ]
        )

        url = reverse('app_auth:login')
        data = {'email': 'user0@tfc.com', 'password': 'iamuser'}
        response = self.client.post(url, data=data)
        token = response.data.get('access', None)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')

    def generate_photo_file(self, color=(0, 155, 0)):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=color)
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_successful_created(self):
        data = {
            'email': 'someuser@tfc.com',
            'password': 'somepassword',
            'first_name': 'First',
            'last_name': 'Last',
            'birth_date': '2001-07-31',
            'mobile': rstr.xeger(PHONE_REGEX),
            'male': True,
            'address': 'My lovely home',
            'is_active': False,
            'avatar': self.generate_photo_file(),
            'date_joined': '2010-12-12',
            'last_login': '2010-12-12T13:27:57',
        }

        response = self.client.post(self.url, data)
        self.assertEqual(
            response.status_code,
            CREATE_RESPONSE['status'],
            msg=prettyStr(response.data)
        )
        self.assertEqual(response.data, CREATE_RESPONSE['data'])
        self.test_list(False, NUM_USER + 1)

    def test_list(self, printOut=True, length=None):
        length = length if length is not None else NUM_USER
        client = APIClient()

        response = client.get(self.url)
        self.assertEqual(
            response.status_code,
            LIST_RESPONSE['status'],
            msg=prettyStr(response.data)
        )
        self.assertEqual(len(response.data), length)
        if printOut:
            prettyPrint(response.data)
        else:
            return response

    def test_editted(self):
        edit_uuid = self.users[0].uuid

        data = {
            'uuid': edit_uuid,
            'old_password': 'iamuser',
            'password': 'newpassword'
        }

        response = self.client.patch(self.url, data)
        self.assertEqual(
            response.status_code,
            EDIT_RESPONSE['status'],
            msg=prettyStr(response.data)
        )

    def test_successful_deleted(self):
        delete_uuid = self.users[0].uuid

        response = self.client.delete(self.url, {'uuid': delete_uuid})
        self.assertEqual(
            response.status_code,
            DELETE_RESPONSE['status'],
            msg=prettyStr(response.data)
        )
        self.assertEqual(response.data, DELETE_RESPONSE['data'])
        response = self.test_list(False, NUM_USER - 1)
