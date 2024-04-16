import unittest
from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable, AccountTable, CourseTable, LabTable
from unittest.mock import patch


class TestCreateCourse(unittest.TestCase):
    def setUp(self):
        self.user1 = UserTable(firstName="John", lastName="Doe", email="email@gmail.com", phone="262-724-8212",
                               address="some address", userType="Instructor")
        self.user1.save()
        self.user1Account = AccountTable(username="johnd", password="password123", userId=self.user1.id)
        self.user1Account.save()

    def test_createCourse_correctly(self):
        AdminAssignmentPage.createCourse(AdminAssignmentPage(), "Course1", self.user1.id)
        course = CourseTable.objects.filter(courseName="Course1").first()

        self.assertEqual((course.courseName, course.instructorId), ("Course1", self.user1.id))

    def test_createCourse_duplicateName(self):
        AdminAssignmentPage.createCourse(AdminAssignmentPage(), "Course1", self.user1.id)
        AdminAssignmentPage.createCourse(AdminAssignmentPage(), "Course1", self.user1.id)
        self.assertEqual(CourseTable.objects.filter(courseName="Course1").count(), 1)

if __name__ == '__main__':
    unittest.main()
