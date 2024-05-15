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


class TestCreateLabSection(unittest.TestCase):
    def setUp(self):
        self.admin_page = AdminAssignmentPage()
        self.course = CourseTable.objects.create(courseName="Test Course")

    def tearDown(self):
        # Clean up the course created during testing
        self.course.delete()

    def test_create_lab_section_success(self):
        result = self.admin_page.createLabSection(courseId=self.course.id, sectionNumber="Lab #001")
        self.assertTrue(result)

        # Verify that lab section is created
        self.assertTrue(SectionTable.objects.filter(name="Lab #001", userCourseJoinId=self.course).exists())

    def test_create_lab_section_invalid_course(self):
        result, msg = self.admin_page.createLabSection(courseId=999, sectionNumber="Lab #001")
        self.assertFalse(result)
        self.assertEqual(msg, "Course does not exist")

    def test_create_lab_section_with_empty_name(self):
        with self.assertRaises(ValueError):
            self.admin_page.createLabSection(courseId=self.course.id, sectionNumber="")

    def test_create_lab_section_with_existing_name(self):
        # Create a lab section with the same name to emulate it already exists
        user = UserTable.objects.create(email="emailer@email.com", firstName="firstName", lastName="lastName")
        joinentry = UserCourseJoinTable.objects.create(courseId=self.course.id, userId=user)
        SectionTable.objects.create(name="Lab #001", userCourseJoinId=joinentry)

        #result, msg = self.admin_page.createLabSection(courseId=self.course, sectionNumber="Lab #001")
        #self.assertFalse(result)
        #self.assertEqual(msg, "Lab section already exists for this course")
        with self.assertRaises(ValueError):
            self.admin_page.createLabSection(courseId=self.course.id, sectionNumber="Lab #001")
        joinentry.delete()
        user.delete()


if __name__ == '__main__':
    unittest.main()
