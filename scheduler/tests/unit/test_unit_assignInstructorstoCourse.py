import unittest
from datetime import datetime

import scheduler.views
from adminCourseManagement import AdminCourseManagementPage
from scheduler.models import UserTable, CourseTable, LabTable, UserCourseJoinTable, SectionTable

from scheduler.views import AdminAccManagement


class AssignInstructorsUnitTest(unittest.TestCase):
    def setUp(self):
        self.app = AdminCourseManagementPage()
        self.user1 = UserTable(firstName="instructor", lastName="instructor", email="insinstructor@uwm.edu",
                               phone="262-555-5555",
                               address="some address", userType="instructor")
        self.user1.save()

        self.user2 = UserTable(firstName="Matt", lastName="Kretsch", email="mattins@uwm.edu",
                               phone="262-213-5555",
                               address="some address", userType="ta")
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
        # Test assigning Instructor with valid data
        self.app.assignInstructorToCourse(self.course1.id, self.user1.id)
        courseJoin = UserCourseJoinTable.objects.filter(courseId=self.course1.id, userId=self.user1).first()
        self.assertIsNotNone(courseJoin)
        self.assertEqual((courseJoin.courseId, courseJoin.userId), (self.course1, self.user1))

    def test_assignIns_UserNotIns(self):
        # Test assigning Instructor with a TA instead of an Instructor
        with self.assertRaises(ValueError):
            self.app.assignInstructorToCourse(self.course1.id, self.user2.id)

    def test_assignIns_noUser(self):
        # Test assigning Instructor with no user specified
        with self.assertRaises(ValueError):
            self.app.assignInstructorToCourse(self.course1.id, "")

    def test_assignIns_noCourse(self):
        # Test assigning Instructor with no course specified
        with self.assertRaises(ValueError):
            self.app.assignInstructorToCourse("", self.user2.id)

    def test_assignIns_duplicateAssignment(self):
        # Test making an assignment that already exists
        self.app.assignInstructorToCourse(self.course1.id, self.user1.id)

        # Test making an assignment that already exists
        with self.assertRaises(ValueError):
            self.app.assignInstructorToCourse(self.course1.id, self.user1.id)


if __name__ == '__main__':
    unittest.main()
