import unittest
from datetime import datetime

import scheduler.views
from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable, CourseTable, LabTable, UserCourseJoinTable, SectionTable


from scheduler.views import AdminAccManagement

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.user1 = UserTable(firstName="instructor", lastName="instructor", email="insinstructor@uwm.edu",
                               phone="262-555-5555",
                               address="some address", userType="instructor")
        self.user1.save()

        self.user2 = UserTable(firstName="Matt", lastName="Kretsch", email="mattins@uwm.edu",
                               phone="262-213-5555",
                               address="some address", userType="instructor")
        self.user2.save()

        self.course1 = CourseTable(courseName="All about Matt", time="10:30am")
        self.course1.save()
        self.course2 = CourseTable(courseName="Soft 361", time="8:30am")
        self.course2.save()

    def tearDown(self):
        # Clean up test data
        self.user1.delete()
        self.user2.delete()
        self.course1.delete()
        self.course2.delete()

    def test_assignIns_correctly(self):
        self.app.assignInstructorToCourse("Course1", "")
        course = CourseTable.objects.get(courseName="Course1")
        self.assertIsNotNone(course)

    def test_createCourse_duplicateName(self):
        self.app.createCourse("Course1", "")
        with self.assertRaises(ValueError):
            self.app.createCourse("Course1", "")
        self.assertEqual(CourseTable.objects.filter(courseName="Course1").count(), 1)

    def test_createCourse_emptyCourseName(self):
        with self.assertRaises(ValueError):
            self.app.createCourse("", "")

    def test_createCourse_withInstructor(self):
        self.app.createCourse("Course1", self.user1.id)
        course = CourseTable.objects.get(courseName="Course1")
        self.assertIsNotNone(course)


if __name__ == '__main__':
    unittest.main()
