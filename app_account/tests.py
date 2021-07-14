from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from freezegun import freeze_time

from rest_framework import status
from rest_framework.test import APIClient

CustomUser = get_user_model()


class GetSelfTests(TestCase):
    url = reverse('app_account:get_self')

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
        client = APIClient()
        data = {
            'email': 'user1@tfc.com',
            'password': 'iamuser1'
        }
        response = client.post(reverse('app_auth:login'), data=data)
        response = client.get(self.url)
        serializer = {
            'last_login': '2016-12-21T23:00:00+07:00',
            'is_superuser': False, 'is_staff': False, 'is_active': True,
            'email': 'user1@tfc.com', 'first_name': 'First', 'last_name': 'Last',
            'birth_date': '2001-07-31',
            'mobile': '0123456789', 'male': True, 'address': 'My lovely home',
            'date_joined': '2016-12-21T23:00:00+07:00',
            'date_updated': '2016-12-21T23:00:00+07:00',
            'groups': [], 'user_permissions': []
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(serializer.items() <= response.data.items())


class ListUserTests(TestCase):
    url = reverse('app_account:list_user')

    # TODO


class CreateUserTests(TestCase):
    url = reverse('app_account:create_user')

    # TODO


class EditUserTests(TestCase):
    url = reverse('app_account:edit_user')

    # TODO


class DeleteUserTests(TestCase):
    url = reverse('app_account:delete_user')

    # TODO


class ListStaffTests(TestCase):
    url = reverse('app_account:list_staff')

    # TODO


class CreateStaffTests(TestCase):
    url = reverse('app_account:create_staff')

    # TODO


class EditStaffTests(TestCase):
    url = reverse('app_account:edit_staff')

    # TODO


class DeleteStaffTests(TestCase):
    url = reverse('app_account:delete_staff')

    # TODO
