from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.urls import reverse

from rest_framework import status
from rest_framework.test import (APIClient, APITestCase)

from app_course.tests import create_course
from master_api.utils import (prettyPrint, prettyStr, compare_dict)
from master_api.views import (
    CREATE_RESPONSE, EDIT_RESPONSE, DELETE_RESPONSE, GET_RESPONSE, LIST_RESPONSE
)
from master_db.models import (ClassMetadata, PHONE_REGEX)

import json
import rstr

CustomUser = get_user_model()
NUM_STUDENT_EACH = 10
NUM_CLASS = 10
teacher_password = make_password('teacherpassword')
student_password = make_password('studentpassword')
special_password = make_password('specialpassword')


def create_class(desc=0, course=None):
    course = course if course is not None else create_course(desc)
    teacher, students = create_teacher_students(desc)

    klass = ClassMetadata(
        course=course,
        name=f'Class-{desc}',
        status=f'Iteration {desc}',
        teacher=teacher,
    )
    klass.save()
    klass.students.add(*students)

    return klass


def create_teacher_students(desc=0, num_students=NUM_STUDENT_EACH):
    # Create teacher
    teacher = CustomUser(
        email=f'teacher{desc}@tfc.com',
        password=teacher_password,
        first_name=f'Class-{desc}',
        last_name='Teacher',
        birth_date='1969-06-09',
        mobile=rstr.xeger(PHONE_REGEX),
        male=True,
        address='Meaningless'
    )
    teacher.save()

    # Create students
    students = []
    for x in range(num_students):
        std = CustomUser(
            email=f'class{desc}_std_{x}@tfc.com',
            password=student_password,
            first_name=f'Class-{desc}',
            last_name=f'Student-{x}',
            birth_date='2001-06-09',
            mobile=rstr.xeger(PHONE_REGEX),
            male=x % 2,
            address='Homeless'
        )
        std.save()
        students.append(std)

    return (teacher, students)


def create_special_student():
    return CustomUser.objects.create(
        email=f'{rstr.xeger(PHONE_REGEX)}@tfc.com',
        password=special_password,
        first_name=f'Special',
        last_name='Student',
        birth_date='1969-06-09',
        mobile=rstr.xeger(PHONE_REGEX),
        male=None,
        address='Definitely not gay'
    )


class ClassTest(APITestCase):
    url = reverse('app_class:class_mgmt')
    client = APIClient()

    def setUp(self):
        # Create course
        self.course = create_course()

        # Create classes
        self.classes = []
        for i in range(NUM_CLASS):
            # Create class
            self.classes.append(create_class(i, self.course))

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
        access_token = response.data.get('token').get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {access_token}')

    def test_successful_create(self):
        teacher, students = create_teacher_students(69)

        data = {
            'course':
                self.course.uuid,
            'name':
                'name',
            'teacher':
                str(teacher.uuid),
            'students':
                str([str(std.uuid) for std in students]).replace("'", '"'),
            'status':
                'published',
            'desc':
                'description',
        }

        response = self.client.post(self.url, data)
        self.assertEqual(
            response.status_code,
            CREATE_RESPONSE['status'],
            msg=prettyStr(response.data)
        )
        self.assertEqual(response.data, CREATE_RESPONSE['data'])

        self.test_list(False, NUM_CLASS + 1)

    def test_successful_deleted(self):
        # Check response
        delete_uuid = self.classes[0].uuid
        response = self.client.delete(self.url, data={'uuid': delete_uuid})
        self.assertEqual(
            response.status_code,
            DELETE_RESPONSE['status'],
            msg=prettyStr(response.data)
        )
        self.assertEqual(response.data, 'Deleted')

        # Check in db through list
        response = self.test_list(False, NUM_CLASS - 1)

        # Check if uuid still exists in db
        self.assertFalse(
            any([res['uuid'] == delete_uuid for res in response.data])
        )

    def test_successful_editted(self):
        teacher, students = create_teacher_students(69)

        edit_uuid = str(self.classes[0].uuid)
        std_uuids = str([str(std.uuid) for std in students]).replace("'", '"')
        data = {
            'uuid': edit_uuid,
            'name': 'Name modified',
            'desc': 'This description has been changed',
            'teacher': str(teacher.uuid),
            'students': std_uuids,
        }

        response = self.client.patch(self.url, data=data)

        self.assertEqual(
            response.status_code,
            EDIT_RESPONSE['status'],
            msg=prettyStr(response.data)
        )

        # Check in db through list
        response = self.test_list(False)

        # Check if course in db has been changed
        res = self.test_successful_get(edit_uuid).data
        data['students'] = json.loads(data['students'])
        res['students'] = json.loads(
            str([str(r['uuid']) for r in res['students']]).replace("'", '"')
        )
        # Check every element
        compare_dict(self, data, res)
        self.assertTrue(
            res['created'] != res['modified'],
            msg=f"\n ----created must not equal modified----\n - "
            f"created: {res['created']} \n - modified: {res['modified']}"
        )

    def test_successful_get(self, get_uuid=None):
        get_uuid = str(self.classes[0].uuid) if get_uuid is None else get_uuid

        response = self.client.get(self.url, data={'uuid': get_uuid})
        self.assertEqual(
            response.status_code,
            GET_RESPONSE['status'],
            msg=prettyStr(response.data)
        )
        self.assertEqual(response.data['uuid'], get_uuid)

        return response

    def test_list(self, printOut=True, length=None):
        url = reverse('app_class:reverse')
        length = length if length is not None else NUM_CLASS

        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            LIST_RESPONSE['status'],
            msg=prettyStr(response.data)
        )
        self.assertEqual(len(response.data), length)

        if printOut:
            print("\n ============List All DB Visualizing============")
            prettyPrint(response.data)
            print("\n ============List All DB Visualizing============")
        else:
            return response

        # Special case for listing student participates in many classes
        std = create_special_student()

        for c in self.classes:
            if int(c.name[-1]) % 3 == 0:
                c.students.add(std)

        student_uuid = std.uuid
        response = self.client.get(url, data={'student_uuid': student_uuid})

        # Check for student presence in every class
        std_classes = [str(c.uuid) for c in std.student_classes.all()]
        res_classes = [str(d['uuid']) for d in response.data]
        compare_dict(self, {'class': std_classes}, {'class': res_classes})

        if printOut:
            print("\n ============List Student's Visualizing============")
            prettyPrint(response.data)
            print("\n ============List Student's Visualizing============")
            print(
                f"Note: All class's name NO. should be divisible by 3 in range from 0 to {NUM_CLASS - 1}"
            )


class ClassStudentTest(APITestCase):
    url = reverse('app_class:student_mgmt')
    client = APIClient()

    def setUp(self):
        # Create course
        self.course = create_course()

        # Create classes
        self.classes = []
        for i in range(NUM_CLASS):
            # Create class
            self.classes.append(create_class(i, self.course))

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
        access_token = response.data.get('token').get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {access_token}')

    def test_successful_addStd(self):
        class_uuid = str(self.classes[0].uuid)
        std_uuid = str([str(create_special_student().uuid)
                        for _ in range(3)]).replace("'", '"')

        response = self.client.patch(
            self.url, data={
                'uuid': class_uuid,
                'student_uuids': std_uuid
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=prettyStr(response.data)
        )

    def test_successful_delStd(self):
        klass = create_class(69)

        data = {
            'uuid':
                str(klass.uuid),
            'student_uuids':
                str([str(std.uuid)
                     for std in klass.students.all()]).replace("'", '"')
        }

        response = self.client.delete(self.url, data=data)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=prettyStr(response.data)
        )
