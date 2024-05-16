import unittest

from django.test import TestCase
from django.urls import reverse
from scheduler.models import UserTable, LabTable, SectionTable, UserLabJoinTable, CourseTable
from django.contrib.auth.models import User


class AssignTAToLabTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='adminpass', email='admin@example.com')
        self.course = CourseTable.objects.create(courseName='taToLabTest')
        self.client.login(username='admin', password='adminpass')
        self.section = SectionTable.objects.create(name="Section 101", courseId=self.course)
        self.lab = LabTable.objects.create(sectionNumber="Lab 01", section=self.section)
        self.ta = UserTable.objects.create(firstName="John", lastName="Doe", email="ta@example.com", userType='ta')
        self.instructor = UserTable.objects.create(firstName="Alice", lastName="Smith", email="instructor@example.com",
                                                   userType='instructor')

    def test_assign_ta_to_lab_success(self):
        response = self.client.post(reverse('courseManagement'), {
            'labId': self.lab.id,
            'userId': self.ta.id,
            'assignTAToLabBtn': 'Submit'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserLabJoinTable.objects.filter(labId=self.lab, userId=self.ta).exists())

    def test_assign_nonexistent_ta_to_lab(self):
        response = self.client.post(reverse('courseManagement'), {
            'labId': self.lab.id,
            'userId': 999,  # Non-existent user ID
            'assignTAToLabBtn': 'Submit'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UserLabJoinTable.objects.filter(labId=self.lab, userId=999).exists())

    def test_assign_ta_to_nonexistent_lab(self):
        response = self.client.post(reverse('courseManagement'), {
            'labId': 999,  # Non-existent lab ID
            'userId': self.ta.id,
            'assignTAToLabBtn': 'Submit'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UserLabJoinTable.objects.filter(labId=999, userId=self.ta).exists())

    def test_assign_non_ta_user_to_lab(self):
        response = self.client.post(reverse('courseManagement'), {
            'labId': self.lab.id,
            'userId': self.instructor.id,
            'assignTAToLabBtn': 'Submit'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UserLabJoinTable.objects.filter(labId=self.lab, userId=self.instructor).exists())

    def test_assign_ta_to_lab_with_no_section(self):
        # Assuming labs must be linked to sections
        response = self.client.post(reverse('courseManagement'), {
            'labId': "",
            'userId': self.ta.id,
            'assignTAToLabBtn': 'Submit'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn("", response.content.decode())


if __name__ == '__main__':
    unittest.main()
