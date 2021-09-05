from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

CustomUser = get_user_model()


class UsersManagersTests(APITestCase):
    def test_create_user(self):
        user = CustomUser.objects.create_user(
            email='user1@tfc.com',
            password='iamuser1',
            first_name='First',
            last_name='Last',
            birth_date='2001-07-31',
            mobile='0123456789',
            # TODO gender='M',
            male=True,
            address='My lovely home'
        )

        self.assertEqual(user.email, 'user1@tfc.com')
        self.assertEqual(user.first_name, 'First')
        self.assertEqual(user.last_name, 'Last')
        self.assertEqual(user.birth_date, '2001-07-31')
        self.assertEqual(user.mobile, '0123456789')
        # TODO self.assertEqual(user.gender, 'M')
        self.assertTrue(user.male)
        self.assertEqual(user.address, 'My lovely home')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNone(user.username)

        with self.assertRaises(TypeError):
            CustomUser.objects.create_user()
        with self.assertRaises(TypeError):
            CustomUser.objects.create_user(email='')
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email='', password="foo")

    def test_create_superuser(self):
        admin_user = CustomUser.objects.create_superuser(
            email='superuser1@tfc.com',
            password='iamsuperuser1',
            first_name='First',
            last_name='Last',
            birth_date='2001-08-31',
            mobile='0123456789',
            # TODO gender='M',
            male=True,
            address='My lovely home'
        )

        self.assertEqual(admin_user.email, 'superuser1@tfc.com')
        self.assertEqual(admin_user.first_name, 'First')
        self.assertEqual(admin_user.last_name, 'Last')
        self.assertEqual(admin_user.birth_date, '2001-08-31')
        self.assertEqual(admin_user.mobile, '0123456789')
        # self.assertEqual(admin_user.gender, 'M')
        self.assertTrue(admin_user.male)
        self.assertEqual(admin_user.address, 'My lovely home')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertIsNone(admin_user.username)

        with self.assertRaises(TypeError):
            CustomUser.objects.create_superuser()
        with self.assertRaises(TypeError):
            CustomUser.objects.create_superuser(email='')
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(
                email='', password='foo', is_superuser=False
            )
