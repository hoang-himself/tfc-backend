from django.http import response
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from master_db.models import Course, ClassMetadata
from master_api.utils import prettyPrint, compare_dict
from master_api.views import (
    CREATE_RESPONSE, EDIT_RESPONSE, DELETE_RESPONSE,
    GET_RESPONSE, LIST_RESPONSE)

from app_course.tests import create_course


CustomUser = get_user_model()
NUM_STUDENT_EACH = 10
NUM_CLASS = 10


def create_class(desc=0, course=None):
    course = course if course is not None else create_course()
    tch_stds = create_teacher_students(desc)

    klass = ClassMetadata(
        course=course,
        name=f'Class-{desc}',
        status=f'Iteration {desc}',
        teacher=tch_stds['teacher'],
    )
    klass.save()
    klass.students.add(*tch_stds['students'])

    return klass


def create_teacher_students(desc=0, num_students=NUM_STUDENT_EACH):
    # Create teacher
    teacher = CustomUser(
        email=f'teacher{desc}@tfc.com', password='teacherpassword',
        first_name=f'Class-{desc}', last_name='Teacher',
        birth_date='1969-06-09', mobile=f'0919877{desc:03d}',
        male=True, address='Meaningless'
    )
    teacher.save()

    # Create students
    students = []
    for x in range(num_students):
        std = CustomUser(
            email=f'class{desc}_std_{x}@tfc.com', password='studentpassword',
            first_name=f'Class-{desc}', last_name=f'Student-{x}',
            birth_date='2001-06-09', mobile=f'0969{desc:03d}{x:03d}',
            male=x % 2, address='Homeless'
        )
        std.save()
        students.append(std)

    return {
        'teacher': teacher,
        'students': students,
    }


class ClassTest(TestCase):
    url = '/api/v1/class/'

    def setUp(self):
        # Create course
        self.course = create_course()

        # Create classes
        self.classes = []
        for i in range(NUM_CLASS):
            # Create class
            self.classes.append(create_class(i, self.course))

    def test_create(self):
        client = APIClient()
        url = self.url + 'create'

        data = {
            'course': self.course.uuid,
            'name': 'name',
            'teacher': self.humans['teacher'].uuid,
            'students': str([str(std.uuid) for std in self.humans['students']]),
            'status': 'published',
            'desc': 'description',
        }

        response = client.post(url, data)
        self.assertEqual(response.status_code, CREATE_RESPONSE['status'])
        self.assertEqual(response.data, CREATE_RESPONSE['data'])

        response = self.test_list(False, NUM_CLASS + 1)

    def test_successful_get(self):
        client = APIClient()
        url = self.url + 'get'
        get_uuid = str(self.classes[0].uuid)

        response = client.get(url, data={'uuid': get_uuid})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['uuid'], get_uuid)

    def test_list(self, printOut=True, length=None):
        client = APIClient()
        url = self.url + 'list'
        length = length if length is not None else NUM_CLASS

        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), length)

        if printOut:
            print("\n ------------List All DB Visualizing------------")
            prettyPrint(response.data)
            print("\n ------------List All DB Visualizing------------")
        else:
            return response

        # Special case for listing student participates in many classes
        std = CustomUser(
            email='special-std@tfc.com', password='specialpassword',
            first_name=f'Special', last_name='Student',
            birth_date='1969-06-09', mobile=f'0987654321',
            male=None, address='Definitely not gay'
        )
        std.save()

        for c in self.classes:
            if int(c.name[-1]) % 3 == 0:
                c.students.add(std)

        student_uuid = std.uuid
        response = client.get(url, data={'student_uuid': student_uuid})

        # Check for student presence in every class
        for d in response.data:
            for c in self.classes:
                if c.uuid == d['uuid']:
                    self.assertTrue(any([student_uuid == std.uuid for std in c.students.all()]),
                                    msg=f"Student with uuid {student_uuid} does not exist in class with uuid {c.uuid}")
                    break

        if printOut:
            print("\n ------------List Student's Visualizing------------")
            prettyPrint(response.data)
            print("\n ------------List Student's Visualizing------------")
            print(
                f"Note: NO. of class's name should be divisible by 3 in range from 0 to {NUM_CLASS - 1}")
