import unittest
from unittest.mock import MagicMock, patch

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse

import scheduler.views
from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable, CourseTable, LabTable, UserCourseJoinTable, SectionTable, UserLabJoinTable, \
    UserSectionJoinTable
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from scheduler.views import AdminAccManagement


class TestEditCourseAcceptance(TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.user1 = UserTable(firstName="Rory", lastName="Christlieb", email="RoCh@gmail.com", phone="123-455-5555",
                               address="some address", userType="admin")
        self.user1.save()
        self.user1Account = User(username="RoryC", password="password", email=self.user1.email)
        self.user1Account.save()
        self.user2 = UserTable(firstName="John", lastName="Doe", email="JDoe@gmail.com", phone="123-456-7890",
                               address="another address", userType="instructor")
        self.user2.save()
        self.user2Account = User(username="John_Doe", password="anonymous", email=self.user2.email)
        self.user2Account.save()

        self.course1 = CourseTable.objects.create(courseName="Computer Science 361", time="MoWeFr 2:00pm-3:00pm")
        self.courseManagement_url = reverse('courseManagement')
        self.home_url = reverse('home')
        self.login_url = reverse('login')

    def tearDown(self):
        self.user1.delete()
        self.user1Account.delete()
        self.user2.delete()
        self.user2Account.delete()
        self.course1.delete()

    def test_courseCourse_page(self):
        # Ensure that the course creation form is rendered correctly
        request = RequestFactory().get(self.courseManagement_url)
        request.user = self.user1Account
        response = scheduler.views.courseManagement(request)
        self.assertEqual(response.status_code, 200)

    def test_courseManagement_redirect_non_admin(self):
        request = RequestFactory().get(self.courseManagement_url)
        request.user = self.user2Account
        response = scheduler.views.courseManagement(request)
        self.assertEqual(response.status_code, 302)

    def test_course_edit_success(self):
        request = RequestFactory().get(self.courseManagement_url)
        request.user = self.user1Account
        response = AdminAccManagement.as_view()(request)
        self.assertEqual(response.status_code, 200)
        data = {
            'editCourseSelect': 1,
            'editName': 'Computer Science 362',
            'editTime': 'TuTh 2:30pm - 3:30pm',
            'editCourseBtn': 'Submit',
        }
        self.client.post(self.courseManagement_url, data, follow=True)
        self.assertTrue(CourseTable.objects.filter(courseName='Computer Science 362').exists())
        self.assertEqual(response.status_code, 200)

    def test_course_edit_failure(self):
        request = RequestFactory().get(reverse('courseManagement'))
        request.user = self.user1Account
        response = AdminAccManagement.as_view()(request)
        self.assertEqual(response.status_code, 200)
        data = {
            'editCourseSelect': 100000000000000,
            'editName': 'Computer Science 362',
            'editTime': 'TuTh 2:30pm - 3:30pm',
            'editCourseBtn': 'Submit',
        }
        response = self.client.post(reverse('courseManagement'), data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CourseTable.objects.filter(courseName='').exists())


if __name__ == '__main__':
    unittest.main()
