from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from freezegun import freeze_time

from rest_framework import status
from rest_framework.test import APIClient

CustomUser = get_user_model()


class GetSelfTests(TestCase):

    @freeze_time("2016-12-21 16:00:00", tz_offset=+7)
    def setUp(self):
        CustomUser.objects.create_user(
            email='user1@tfc.com', password='iamuser1',
            first_name='First', last_name='Last',
            birth_date='2001-07-31', mobile='0123456789',
            male=True, address='My lovely home',
        )

    @freeze_time("2016-12-21 16:00:00", tz_offset=+7)
    def test_no_filter(self):
        url = reverse('app_account:get-self')
        client = APIClient()
        data = {
            'email': 'user1@tfc.com',
            'password': 'iamuser1'
        }
        response = client.post(reverse('app_auth:login'), data=data)
        response = client.get(url)
        serializer = {
            'email': 'user1@tfc.com', 'first_name': 'First',
            'last_name': 'Last', 'birth_date': '2001-07-31',
            'mobile': '0123456789', 'male': True, 'address': 'My lovely home',
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(serializer.items() <= response.data.items())

    @freeze_time("2016-12-21 16:00:00", tz_offset=+7)
    def test_fragmented_filter(self):
        url = '{}?{}'.format(reverse('app_account:get-self'), '&'.join(
            [
                'filter=email',
                'filter=mobile',
                'filter=birth_date',
            ]  # /api/v1/account/get?filter=email&filter=mobile&filter=birth_date
        ))
        client = APIClient()
        data = {
            'email': 'user1@tfc.com',
            'password': 'iamuser1'
        }
        response = client.post(reverse('app_auth:login'), data=data)
        response = client.get(url)
        serializer = {
            'email': 'user1@tfc.com',
            'mobile': '0123456789',
            'birth_date': '2001-07-31',
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer, response.data)


class ListUserTests(TestCase):
    url = reverse('app_account:list-user')

    # TODO


class CreateUserTests(TestCase):
    url = reverse('app_account:create-user')

    # TODO


class EditUserTests(TestCase):
    url = reverse('app_account:edit-user')

    # TODO


class DeleteUserTests(TestCase):
    url = reverse('app_account:delete-user')

    # TODO


class ListStaffTests(TestCase):
    url = reverse('app_account:list-staff')

    # TODO


class CreateStaffTests(TestCase):
    url = reverse('app_account:create-staff')

    # TODO


class EditStaffTests(TestCase):
    url = reverse('app_account:edit-staff')

    # TODO


class DeleteStaffTests(TestCase):
    url = reverse('app_account:delete-staff')

    # TODO
