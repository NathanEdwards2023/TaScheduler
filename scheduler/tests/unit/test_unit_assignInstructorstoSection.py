import unittest
from datetime import datetime

import scheduler.views
from adminAssignmentPage import AdminAssignmentPage
from instructorCourseManagement import InstructorCourseManagementPage
from scheduler.models import UserTable, CourseTable, LabTable, UserCourseJoinTable, SectionTable, UserSectionJoinTable

from scheduler.views import AdminAccManagement


class AssignInstructorsToSectionUnitTest(unittest.TestCase):
    def setUp(self):
        self.app = InstructorCourseManagementPage()
        self.user1 = UserTable(firstName="instructor", lastName="instructor", email="insinstructor2@uwm.edu",
                               phone="262-555-5555",
                               address="some address", userType="instructor")
        self.user1.save()

        self.user2 = UserTable(firstName="Matt", lastName="Kretsch", email="mattins2@uwm.edu",
                               phone="262-213-5555",
                               address="some address", userType="ta")
        self.user2.save()

        self.course1 = CourseTable(courseName="All about Matt", time="10:30am")
        self.course1.save()
        self.course2 = CourseTable(courseName="Soft 361", time="8:30am")
        self.course2.save()

        self.section1 = SectionTable(name="Unit Test section", courseId=self.course1, time="9:30AM")
        self.section1.save()

    def tearDown(self):
        # Clean up test data
        self.user1.delete()
        self.user2.delete()
        self.course1.delete()
        self.course2.delete()
        self.section1.delete()

    def test_assignIns_correctly(self):
        # Test assigning Instructor with valid data
        self.app.assignInsToSection(self.section1.id, self.user1.id)
        sectionJoin = UserSectionJoinTable.objects.filter(sectionId=self.section1, userId=self.user1).first()
        self.assertIsNotNone(sectionJoin)
        self.assertEqual((sectionJoin.sectionId, sectionJoin.userId), (self.section1, self.user1))

    def test_assignIns_UserNotIns(self):
        # Test assigning Instructor with a TA instead of an Instructor
        with self.assertRaises(ValueError):
            self.app.assignInsToSection(self.section1.id, self.user2.id)

    def test_assignIns_noUser(self):
        # Test assigning Instructor to section with no user specified
        with self.assertRaises(ValueError):
            self.app.assignInsToSection(self.section1.id, "")

    def test_assignIns_noSection(self):
        # Test assigning Instructor with no section specified
        with self.assertRaises(ValueError):
            self.app.assignInsToSection("", self.user1.id)

    def test_assignIns_duplicateAssignment(self):
        # Test making a section assignment that already exists
        self.app.assignInsToSection(self.section1.id, self.user1.id)

        # Test making an assignment that already exists
        with self.assertRaises(ValueError):
            self.app.assignInsToSection(self.section1.id, self.user1.id)


if __name__ == '__main__':
    unittest.main()
