from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CustomUser = get_user_model()


class ListUserTests(TestCase):
    url = reverse('list_user')

    # TODO


class CreateUserTests(TestCase):
    url = reverse('create_user')

    # TODO


class GetUserTests(TestCase):
    url = reverse('get_user')

    # TODO


class EditUserTests(TestCase):
    url = reverse('edit_user')

    # TODO


class DeleteUserTests(TestCase):
    url = reverse('delete_user')

    # TODO


class ListStaffTests(TestCase):
    url = reverse('list_staff')

    # TODO


class CreateStaffTests(TestCase):
    url = reverse('create_staff')

    # TODO


class GetStaffTests(TestCase):
    url = reverse('get_staff')

    # TODO


class EditStaffTests(TestCase):
    url = reverse('edit_staff')

    # TODO


class DeleteStaffTests(TestCase):
    url = reverse('delete_staff')

    # TODO
