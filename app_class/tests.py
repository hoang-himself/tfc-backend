from django.http import response
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from master_db.models import Course, ClassMetadata
from master_api.utils import prettyPrint


CustomUser = get_user_model()
NUM_STUDENT_EACH = 10
NUM_CLASS = 10


class ClassTest(TestCase):
    url = '/api/v1/class/'

    def setUp(self):
        # Create course
        course = Course(
            name='Dummy Course',
            duration=69,
            desc='Dummy Course description'
        )
        course.save()
        course.tags.add('this', 'is', 'a', 'freaking', 'dummy', 'course')
        self.course = course

        #Create classes
        self.classes = []
        for i in range(NUM_CLASS):
            # Create teacher
            teacher = CustomUser(
                email=f'teacher{i}@tfc.com', password='teacherpassword',
                first_name=f'Class-{i}', last_name='Teacher',
                birth_date='1969-06-09', mobile=f'0919877{i:03d}',
                male=True, address='Meaningless'
            )
            teacher.save()

            # Create students
            students = []
            for x in range(NUM_STUDENT_EACH):
                std = CustomUser(
                    email=f'class{i}_std_{x}@tfc.com', password='studentpassword',
                    first_name=f'Class-{i}', last_name=f'Student-{x}',
                    birth_date='2001-06-09', mobile=f'0969{i:03d}{x:03d}',
                    male=x % 2, address='Homeless'
                )
                std.save()
                students.append(std)

            # Finalize class
            klass = ClassMetadata(
                course=course,
                name=f'Class-{i}',
                status=f'Iteration {i}',
                teacher=teacher,
            )
            klass.save()
            klass.students.add(*students)

            self.classes.append(klass)

    def compare_dict(self, dict1, dict2):
        for key, value in dict1.items():
            if isinstance(value, list):
                value = set(value)
                dict2[key] = set(dict2[key])
            self.assertTrue(
                value == dict2[key], msg=f"{key}: {value} <-> {dict2[key]} => {value == dict2[key]}")

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

        # Special case for listing student participates in many classes
        std = CustomUser(
            email='special-std@tfc.com', password='specialpassword',
            first_name=f'Special', last_name='Student',
            birth_date='1969-06-09', mobile=f'0987654321',
            male=None, address='Definitely not gay'
        )
        std.save()
        
        for c in self.classes:
            c.students.add(std)

        student_uuid = str(std.uuid)
        response = client.get(url, data={'student_uuid': student_uuid})
        
        if printOut:
            print("\n ------------List Student's Visualizing------------")
            prettyPrint(response.data)
            print("\n ------------List Student's Visualizing------------")

        return response
        
        
