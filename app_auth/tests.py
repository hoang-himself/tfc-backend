from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CustomUser = get_user_model()


class LoginTests(TestCase):
    url = reverse('login')

    def setUp(self):
        CustomUser.objects.create_user(
            email='user1@tfc.com', password='iamuser1',
            first_name='First', last_and_mid_name='Last',
            birth_date='2001-07-31', mobile='0123456789',
            male=True, address='My lovely home'
        )

    def test_anon(self):
        client = APIClient()
        response = client.post(self.url)
        serializer = {
            'detail': {
                'email': 'This field is required.',
                'password': 'This field is required.'
            }
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, serializer)

    def test_no_password(self):
        client = APIClient()
        data = {
            'email': 'user1@tfc.com'
        }
        response = client.post(self.url, data=data)
        serializer = {
            'detail': {
                'password': 'This field is required.'
            }
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, serializer)

    def test_no_email(self):
        client = APIClient()
        data = {
            'password': 'iamuser1'
        }
        response = client.post(self.url, data=data)
        serializer = {
            'detail': {
                'email': 'This field is required.'
            }
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, serializer)

    def test_success(self):
        client = APIClient()
        data = {
            'email': 'user1@tfc.com',
            'password': 'iamuser1'
        }
        response = client.post(self.url, data=data)
        csrf_token = response.cookies.get('csrftoken')
        access_token = response.cookies.get('accesstoken')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(csrf_token)
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(response.data.get('detail').get('refresh_token'))


class RefreshTests(TestCase):
    url = reverse('refresh')

    def setUp(self):
        CustomUser.objects.create_user(
            email='user1@tfc.com', password='iamuser1',
            first_name='First', last_and_mid_name='Last',
            birth_date='2001-07-31', mobile='0123456789',
            male=True, address='My lovely home'
        )

    def test_no_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        response = client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_access(self):
        client = APIClient()
        response = client.post(self.url)
        serializer = {
            'detail': 'User not logged in.'
        }

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, serializer)

    def test_success(self):
        client = APIClient()
        data = {
            'email': 'user1@tfc.com',
            'password': 'iamuser1'
        }
        response = client.post(reverse('login'), data=data)
        refresh_token = response.data.get('detail').get('refresh_token')

        data = {
            'refresh_token': refresh_token
        }
        response = client.post(self.url, data=data)
        serializer = {
            'detail': 'Ok'
        }
        access_token = response.cookies.get('accesstoken')

        self.assertIsNotNone(access_token)
        self.assertEqual(response.data, serializer)


class LogoutTests(TestCase):
    url = reverse('logout')
    client = APIClient()

    pass
