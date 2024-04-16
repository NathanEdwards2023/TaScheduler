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

    def test_createCourse_noInstructor(self):
        #returns true if invalid instructor ID
        with self.assertRaises(Exception):
            AdminAssignmentPage.createCourse(AdminAssignmentPage(), "Course10", 10)

class TestCreateAccount(unittest.TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()

    def test_createAccountSuccess(self):
        result = self.app.createAccount('user', 'testuser@example.com', 'password')
        self.assertIsNone(result)

    def test_createAccountEmptyUsername(self):
        with self.assertEqual(ValueError):
            self.app.createAccount('', 'testuser@example.com', 'password')

    def test_createAccountWithWeakPassword(self):
        with self.assertEqual(ValueError):
            self.app.createAccount('user', 'testuser@example.com', 'pass')

    def test_createAccountWithInvalidEmail(self):
        with self.assertRaises(ValueError):
            self.app.createAccount('user', 'not-an-email', 'password')

    def test_createAccountWithExistingUser(self):
        self.app.createAccount('user', 'testuser@example.com', 'password')
        with self.assertRaises(Exception) as context:
            self.app.createAccount('user', 'testuser@example.com', 'password')
            self.assertIn("User already exists", str(context.exception))


class TestEditAccount(unittest.TestCase):
    def setUp(self):
        self.self = AdminAssignmentPage()
        user = UserTable(firstName="John", lastName="Doe", email="email@gmail.com", phone="262-724-8212",
                         address="some address", userType="Instructor")
        user.save()
        userAccount = AccountTable(username="johnD", password="password123", userId=user.id)
        userAccount.save()

    def test_editAccount(self):
        newUser = AdminAssignmentPage.editAccount(self, 0, "newemail@uwm.com", "1234567890", "123 street", "TA")
        self.assertEqual(newUser,
                         UserTable(firstName="John", lastName="Doe", email="newemail@uwm.com", phone="1234567890",
                                   address="123 street", role="TA"))

    def test_editMissingAccount(self):
        self.assertRaises(ValueError,
                          AdminAssignmentPage.editAccount(self, 5, "newemail@uwm.com", "1234567890", "123 street", "TA"))


class TestDeleteAccount(unittest.TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()

    def test_deleteAccount(self):
        self.app.createAccount("testuser", "testuser@example.com", "password")
        result = self.app.deleteAccount(user_id=0)
        self.assertEqual(True, result)

    def test_deleteAccountInvalidID(self):
        self.app.createAccount("testuser", "testuser@example.com", "password")
        result = self.app.deleteAccount(user_id=1)
        self.assertEqual(False, result)

    def test_deleteTwoAccount(self):
        self.app.createAccount("testuser", "testuser@example.com", "password")
        self.app.deleteAccount(user_id=0)
        self.app.createAccount("testuser2", "testuser2@example.com", "password2")
        result = self.app.deleteAccount(user_id=1)
        self.assertEqual(True, result)

    def test_invalidArg(self):
        self.app.createAccount("testuser", "testuser@example.com", "password")
        with self.assertRaises(TypeError):
            self.app.deleteAccount(user_id="Zero")

    def test_noAccountsLeft(self):
        with self.assertRaises(ValueError):
            self.app.deleteAccount(user_id=0)


if __name__ == '__main__':
    unittest.main()
