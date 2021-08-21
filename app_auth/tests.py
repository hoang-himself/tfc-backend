from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import (APIClient, APITestCase)

CustomUser = get_user_model()


class AuthTests(APITestCase):
    url = reverse('app_auth:login')
    client = APIClient()

    def setUp(self):
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

    def test_anon(self):
        response = self.client.post(self.url)
        serializer = {
            'email': 'This field is required.',
            'password': 'This field is required.'
        }

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, serializer)

    def test_no_password(self):
        data = {'email': 'user1@tfc.com'}
        response = self.client.post(self.url, data=data)
        serializer = {'password': 'This field is required.'}

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, serializer)

    def test_no_email(self):
        data = {'password': 'iamuser1'}
        response = self.client.post(self.url, data=data)
        serializer = {'email': 'This field is required.'}

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, serializer)

    def test_success(self):
        data = {'email': 'user1@tfc.com', 'password': 'iamuser1'}
        response = self.client.post(self.url, data=data)
        access_token = response.data.get('token').get('access')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(response.data.get('token').get('refresh'))


class RefreshTests(APITestCase):
    url = reverse('app_auth:refresh')
    client = APIClient()

    def setUp(self):
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

    def test_no_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        response = client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_access(self):
        response = self.client.post(self.url)
        serializer = {'refresh': 'This field is required.'}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, serializer)

    def test_success(self):
        data = {'email': 'user1@tfc.com', 'password': 'iamuser1'}
        response = self.client.post(reverse('app_auth:login'), data=data)
        refresh_token = response.data.get('token').get('refresh')

        data = {'refresh': refresh_token}
        response = self.client.post(self.url, data=data)
        access_token = response.data.get('token').get('access')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(access_token)


class LogoutTests(APITestCase):
    url = reverse('app_auth:logout')
    client = APIClient()

    def setUp(self):
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

    def temp_test(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)


"""
    def test_no_access(self):
        client = APIClient()
        response = client.delete(self.url)
        serializer = {
            'detail': 'User not logged in.'
        }

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data, serializer)

    def test_success(self):
        client = APIClient()
        data = {
            'email': 'user1@tfc.com',
            'password': 'iamuser1'
        }
        response = client.post(reverse('app_auth:login'), data=data)
        refresh_token = response.data.get('detail').get('refresh_token')

        data = {
            'refresh_token': refresh_token
        }
        response = client.delete(self.url, data=data)
        serializer = {
            'detail': 'Ok'
        }
        access_token =response.data.get('token').get('access')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(access_token, '')
        self.assertEqual(response.data, serializer)
"""
