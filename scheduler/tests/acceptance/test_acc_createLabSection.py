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


class TestCreateLabSectionAcceptance(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create(username='admin', is_staff=True)
        self.client.force_login(self.admin_user)
        self.admin_page = AdminAssignmentPage()
        self.course = CourseTable.objects.create(courseName="Test Course")

    def tearDown(self):
        # Clean up the course created during testing
        self.course.delete()

    def test_create_lab_section_acceptance(self):
        # Make a request to create a lab section
        response = self.client.post(reverse('create_lab_section'), {'courseId': self.course.id, 'sectionNumber': 'Lab #001'})

        # Verify that lab section is created
        self.assertTrue(SectionTable.objects.filter(name="Lab #001", userCourseJoinId=self.course).exists())
        self.assertEqual(response.status_code, 200)

    def test_create_lab_section_invalid_course_acceptance(self):
        # Make a request to create a lab section with an invalid course ID
        response = self.client.post(reverse('create_lab_section'), {'courseId': 999, 'sectionNumber': 'Lab #001'})

        # Verify that the response indicates failure and no lab section is created
        self.assertEqual(response.status_code, 404)  # or whatever status code indicates failure
        self.assertFalse(SectionTable.objects.filter(name="Lab #001", userCourseJoinId=self.course).exists())

    def test_create_lab_section_with_existing_name_acceptance(self):
        # Create a lab section with the same name to emulate it already exists
        SectionTable.objects.create(name="Lab #001", userCourseJoinId=self.course)

        # Make a request to create a lab section with the same name
        response = self.client.post(reverse('create_lab_section'),
                                    {'courseId': self.course.id, 'sectionNumber': 'Lab #001'})

        # Verify that the response indicates failure and no duplicate lab section is created
        self.assertEqual(response.status_code, 400)  # or whatever status code indicates failure
        self.assertEqual(SectionTable.objects.filter(name="Lab #001", userCourseJoinId=self.course).count(), 1)

    def test_create_lab_section_with_empty_name_acceptance(self):
        # Make a request to create a lab section with an empty name
        response = self.client.post(reverse('create_lab_section'), {'courseId': self.course.id, 'sectionNumber': ''})

        # Verify that the response indicates failure and no lab section is created
        self.assertEqual(response.status_code, 400)  # or whatever status code indicates failure
        self.assertFalse(SectionTable.objects.filter(userCourseJoinId=self.course).exists())


if __name__ == '__main__':
    unittest.main()
