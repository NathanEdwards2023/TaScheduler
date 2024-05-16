
import unittest
from django.contrib.auth.models import User

from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable, CourseTable, UserCourseJoinTable


class TestEditCourse(unittest.TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.user1 = UserTable(firstName="Rory", lastName="Christlieb", email="RC@Sample.com", phone="123-455-5555",
                               address="some address", userType="instructor")
        self.user1.save()
        self.user1Account = User(username="RoryC", password="password", email=self.user1.email)
        self.user1Account.save()
        self.user2 = UserTable(firstName="John", lastName="Doe", email="JDoe@gmail.com", phone="123-456-7890",
                               address="another address", userType="instructor")
        self.user2.save()
        self.user2Account = User(username="John_Doe", password="anonymous", email=self.user2.email)
        self.user2Account.save()
        self.course1 = CourseTable(courseName="Computer Science 361", time="MoWeFr 2:00pm-3:00pm")
        self.course1.save()
        join_table = UserCourseJoinTable(courseId=self.course1, userId=self.user1)
        join_table.save()

    def tearDown(self):
        self.user1.delete()
        self.user1Account.delete()
        self.user2.delete()
        self.user2Account.delete()
        self.course1.delete()

    def test_editCourse_success(self):
        newCourseName = 'Computer Science 362'
        newTime = 'TuTh 2:30pm - 3:30pm'
        self.app.editCourse(self.course1.id, newCourseName, self.user2.id, newTime)
        editedCourse = CourseTable.objects.get(id=self.course1.id)
        self.assertEqual(editedCourse.courseName, newCourseName)
        self.assertEqual(editedCourse.time, newTime)

    def test_editCourse_nonexistentCourse(self):
        with self.assertRaises(ValueError):
            self.app.editCourse(999999, 'Computer Science 362', self.user1.id, 'TuTh 2:30pm - 3:30pm')

    def test_editCourse_emptyCourseName(self):
        with self.assertRaises(ValueError):
            self.app.editCourse(self.course1.id, '', self.user1.id, 'TuTh 2:30pm - 3:30pm')

    def test_editCourse_noActualChanges(self):
        newCourseName = 'Computer Science 361'
        newTime = 'MoWeFr 2:00pm - 3:00pm'
        self.app.editCourse(self.course1.id, newCourseName, self.user1.id, newTime)
        editedCourse = CourseTable.objects.get(id=self.course1.id)
        self.assertEqual(editedCourse.courseName, newCourseName)
        self.assertEqual(editedCourse.time, newTime)


if __name__ == '__main__':
    unittest.main()

