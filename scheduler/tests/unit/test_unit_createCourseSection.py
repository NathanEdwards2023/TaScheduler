import unittest
from datetime import datetime

from django.contrib.auth.models import User
from django.db import IntegrityError

import scheduler.views
from adminAssignmentPage import AdminAssignmentPage
from adminSectionManagement import AdminSectionManagementPage
from scheduler.models import UserTable, CourseTable, LabTable, UserCourseJoinTable, SectionTable

from scheduler.views import AdminAccManagement


class CreateCourseSectionUnitTest(unittest.TestCase):
    def setUp(self):
        self.app = AdminSectionManagementPage()
        self.user1 = UserTable(firstName="matt", lastName="matt", email="mattNew9@gmail.com", phone="262-555-5555",
                               address="some address", userType="instructor")
        self.user1.save()
        self.user1Account = User(username="matt9", password="e121dfa91w", email=self.user1.email)
        self.user1Account.save()

        self.course1 = CourseTable(courseName="UnitTestCourse")
        self.course1.save()

    def tearDown(self):
        # Clean up test data
        self.user1Account.delete()
        self.user1.delete()
        self.course1.delete()

    def test_createSection_correctly(self):
        # Test creating a section with valid input
        section_name = "ValidSection"
        self.app.createSection(section_name, self.course1.id, "10:30AM")
        section = SectionTable.objects.filter(name=section_name, courseId=self.course1).first()

        self.assertIsNotNone(section)
        self.assertEqual(section.name, section_name)

    def test_createSection_CourseNonExisting(self):
        # Test creating a section with a non-existing course ID
        with self.assertRaises(ValueError):
            self.app.createSection("SectionUnitTest1", 9999, "1:00AM")

    def test_createSection_emptySectionName(self):
        # Test creating a section with an empty section name
        with self.assertRaises(ValueError):
            self.app.createSection("", self.course1.id, "10:30AM")

    def test_createSection_duplicateName(self):
        # Test creating a section with a duplicate name within the same course
        section_name = "DuplicateSection"
        self.app.createSection(section_name, self.course1.id, "10:30AM")

        # Attempt to create another section with the same name in the same course
        with self.assertRaises(ValueError):
            self.app.createSection(section_name, self.course1.id, "10:30AM")


if __name__ == '__main__':
    unittest.main()
