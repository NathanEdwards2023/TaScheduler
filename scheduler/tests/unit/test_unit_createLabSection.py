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
        self.assertTrue(SectionTable.objects.filter(name="Lab #001").exists())

    def test_create_lab_section_invalid_course(self):
        with self.assertRaises(ValueError):
            self.admin_page.createLabSection(courseId=999, sectionNumber="Lab #001")

    def test_create_lab_section_with_empty_name(self):
        with self.assertRaises(ValueError):
            self.admin_page.createLabSection(courseId=self.course.id, sectionNumber="")

    def test_create_lab_section_with_existing_name(self):
        # Create a lab section with the same name to emulate it already exists
        section = SectionTable.objects.create(name="Lab #001", courseId=self.course)
        lab = LabTable.objects.create(sectionNumber="Lab #001", section=section)

        with self.assertRaises(ValueError):
            self.admin_page.createLabSection(courseId=self.course.id, sectionNumber="Lab #001")
        section.delete()
        lab.delete()

if __name__ == '__main__':
    unittest.main()
