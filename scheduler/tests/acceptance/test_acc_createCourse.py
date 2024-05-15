import unittest
from unittest.mock import MagicMock, patch

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse

import scheduler.views
from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable, CourseTable, LabTable, UserCourseJoinTable, SectionTable, UserLabJoinTable, UserSectionJoinTable
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from scheduler.views import AdminAccManagement

class TestCreateCourseAcc(TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.user1 = UserTable(firstName="adminTest", lastName="adminTest", email="adminTest@gmail.com",
                               phone="adminTest",
                               address="adminTest", userType="admin")
        self.user1.save()
        self.user1Account = User(username="adminTest", password="adpassword", email=self.user1.email)
        self.user1Account.save()

        self.user2 = UserTable(firstName="deleteTest", lastName="deleteTest", email="deleteTest@gmail.com",
                               phone="deleteTest",
                               address="deleteTest", userType="ta")
        self.user2.save()
        self.user2Account = User(username="deleteTest", password="delpassword", email=self.user2.email)
        self.user2Account.save()

        user2 = UserTable(firstName="Jeff", lastName="Thompson", email="nonadmin@gmail.com", phone="5484651456",
                          address="123 street", userType="instructor")
        user2.save()
        userAccount2 = User(username="JeffT", password="password123", email=user2.email)
        userAccount2.save()

    def tearDown(self):
        # Clean up test data
        self.user1.delete()
        self.user1Account.delete()
        self.user2.delete()
        self.user2Account.delete()

    def test_courseCourse_page(self):
        # Ensure that the course creation form is rendered correctly
        request = RequestFactory().get(reverse('courseManagement'))
        request.user = self.user1Account

        response = scheduler.views.courseManagement(request)

        self.assertEqual(response.status_code, 200)

    def test_courseManagement_redirect_non_admin(self):
        # Ensure that non-admin users are redirected to the home page when trying to access courseManagement
        request = RequestFactory().get(reverse('courseManagement'))
        request.user = self.user2Account

        response = scheduler.views.courseManagement(request)

        self.assertEqual(response.status_code, 302)  # redirects

    def test_course_creation(self):
        # Create a test instructor
        instructor = UserTable.objects.create(firstName="John", lastName="Doe", email="john@example.com",
                                              phone="1234567890", address="123 Main St", userType="instructor")
        self.client.login(username="adminTest", password="adpassword")
        # Ensure that a course can be created
        data = {
            'courseName': 'New Course',
            'instructorSelect': instructor.id,
            'createCourseBtn': 'Submit',  # button used

        }
        response = self.client.post(reverse('courseManagement'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CourseTable.objects.filter(courseName='New Course', instructorId=instructor).exists())

    def test_invalid_course_creation(self):
        # Ensure that an invalid course cannot be created
        data = {
            'courseName': '',  # Invalid empty course name
            'instructorSelect': 9999,  # Invalid instructor ID
        }
        response = self.client.post(reverse('courseManagement'), data)
        self.assertEqual(response.status_code, 302)  # redirects to self
        self.assertFalse(CourseTable.objects.filter(courseName='').exists())

if __name__ == '__main__':
    unittest.main()
