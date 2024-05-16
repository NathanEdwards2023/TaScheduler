from django.test import TestCase
from django.urls import reverse
from scheduler.models import UserTable, CourseTable, UserCourseJoinTable
from django.contrib.auth.models import User


class AssignTAToCourseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='adminpass', email='admin@example.com')
        self.client.login(username='admin', password='adminpass')
        self.course = CourseTable.objects.create(courseName="Data Structures")
        self.ta = UserTable.objects.create(firstName="John", lastName="Doe", email="ta@example.com", userType='ta')
        self.instructor = UserTable.objects.create(firstName="Alice", lastName="Smith", email="instructor@example.com",
                                                   userType='instructor')

    def test_assign_ta_to_course_success(self):
        response = self.client.post(reverse('courseManagement'), {
            'courseId': self.course.id,
            'userId': self.ta.id,
            'assignTAToCourseBtn': 'Submit'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserCourseJoinTable.objects.filter(courseId=self.course, userId=self.ta).exists())

    def test_assign_nonexistent_ta(self):
        response = self.client.post(reverse('courseManagement'), {
            'courseId': self.course.id,
            'userId': 999,  # Non-existent user ID
            'assignTAToCourseBtn': 'Submit'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UserCourseJoinTable.objects.filter(courseId=self.course, userId=999).exists())

    def test_assign_ta_to_nonexistent_course(self):
        response = self.client.post(reverse('courseManagement'), {
            'courseId': 999,  # Non-existent course ID
            'userId': self.ta.id,
            'assignTAToCourseBtn': 'Submit'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UserCourseJoinTable.objects.filter(courseId=999, userId=self.ta).exists())

    def test_assign_non_ta_user(self):
        response = self.client.post(reverse('courseManagement'), {
            'courseId': self.course.id,
            'userId': self.instructor.id,
            'assignTAToCourseBtn': 'Submit'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UserCourseJoinTable.objects.filter(courseId=self.course, userId=self.instructor).exists())


if __name__ == '__main__':
    unittest.main()
