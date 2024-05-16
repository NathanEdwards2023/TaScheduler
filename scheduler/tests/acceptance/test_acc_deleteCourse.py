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


class TestDeleteCourseAcceptance(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create(username='admin', is_staff=True)
        self.client.force_login(self.admin_user)
        self.admin_page = AdminAssignmentPage()

        # Create a course
        self.course = CourseTable.objects.create(courseName="Test Course")

        # Create users
        self.user1 = UserTable.objects.create(email="user01@example.com")
        self.user2 = UserTable.objects.create(email="user02@example.com")

        # Create user-course associations
        self.user_course1 = UserCourseJoinTable.objects.create(courseId=self.course, userId=self.user1)
        self.user_course2 = UserCourseJoinTable.objects.create(courseId=self.course, userId=self.user2)

        # Create sections associated with the course
        self.section1 = SectionTable.objects.create(name="Section 1", userCourseJoinId=self.user_course1)
        self.section2 = SectionTable.objects.create(name="Section 2", userCourseJoinId=self.user_course2)

        # Create lab sections associated with the course
        self.lab1 = LabTable.objects.create(sectionNumber="Lab 001", sectionId=self.section1)
        self.lab2 = LabTable.objects.create(sectionNumber="Lab 002", sectionId=self.section2)

    def tearDown(self):
        # Clean up after each test by deleting created objects
        self.course.delete()
        self.lab1.delete()
        self.lab2.delete()
        self.user_course1.delete()
        self.user_course2.delete()
        self.user1.delete()
        self.user2.delete()

    def test_delete_course_acceptance(self):
        # Make a request to delete the course
        response = self.client.post(reverse('delete_course'), {'id': self.course.id})

        # Verify that the course is deleted and associated objects are also deleted
        self.assertFalse(CourseTable.objects.filter(id=self.course.id).exists())
        self.assertFalse(UserCourseJoinTable.objects.filter(courseId=self.course).exists())
        self.assertFalse(SectionTable.objects.filter(name="Section 1").exists())
        self.assertFalse(SectionTable.objects.filter(name="Section 2").exists())
        self.assertEqual(response.status_code, 200)

    def test_delete_course_not_found_acceptance(self):
        # Make a request to delete a course that does not exist
        response = self.client.post(reverse('delete_course'), {'id': 999})

        # Verify that the response indicates failure and no changes are made
        self.assertEqual(response.status_code, 404)  # or whatever status code indicates failure
        self.assertTrue(CourseTable.objects.filter(id=self.course.id).exists())  # Course should still exist


if __name__ == '__main__':
    unittest.main()
