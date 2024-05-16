import unittest
from django.test import RequestFactory
from django.contrib.auth.models import User

import scheduler.views
from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable, CourseTable, UserCourseJoinTable, SectionTable
from django.test import TestCase
from django.urls import reverse


class TestAssignInstructorToCourse(TestCase):
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)
        self.client = None

    def setUp(self):
        self.app = AdminAssignmentPage()

        self.user1 = UserTable(firstName="adminTest", lastName="adminTest", email="adminTest@gmail.com",
                               phone="adminTest",
                               address="adminTest", userType="admin")
        self.user1.save()
        self.user1Account = User(username="adminTest", password="adpassword", email=self.user1.email)
        self.user1Account.save()

        self.user2 = UserTable(firstName="matt", lastName="matt", email="mattNew@gmail.com", phone="262-555-5555",
                               address="some address", userType="instructor")
        self.user2.save()
        self.user2Account = User(username="matt2", password="e121dfa91w", email=self.user2.email)
        self.user2Account.save()

        self.course1 = CourseTable(courseName="unitTest")
        self.course1.save()

    def tearDown(self):
        # Clean up test data
        self.course1.delete()
        self.user1.delete()
        self.user1Account.delete()
        self.user2.delete()
        self.user2Account.delete()

    def test_adminCourseManagement_Admin(self):
        request = RequestFactory().get(reverse('courseManagement'))  # Use reverse to get the URL
        request.user = self.user1Account
        response = scheduler.views.courseManagement(request)

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

    def test_adminCourseManagement_Instructor(self):
        request = RequestFactory().get(reverse('courseManagement'))  # Use reverse to get the URL
        request.user = self.user2Account

        response = scheduler.views.courseManagement(request)

        # Check if the response status code Redirect
        self.assertEqual(response.status_code, 302)

    def test_adminCourseManagement_assignInstructor(self):
        data = {
            'courseSelect': self.course1.id,
            'instructorSelect': self.user2.id,
            'assignBtn': 'Assign'
        }
        request = RequestFactory().post(reverse('courseManagement'), data=data)
        request.user = self.user1Account

        scheduler.views.courseManagement(request)

        self.assertTrue(UserCourseJoinTable.objects.filter(userId=self.user2, courseId=self.course1).exists())


if __name__ == '__main__':
    unittest.main()
