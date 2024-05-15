import unittest
from datetime import datetime

from django.contrib.auth.models import User

import scheduler.views
from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable, CourseTable, LabTable, UserCourseJoinTable, SectionTable


from scheduler.views import AdminAccManagement
class TestDeleteAccount(unittest.TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        # user 1
        self.user1 = UserTable(firstName="John", lastName="Doe", email="John@gmail.com", phone="262-724-8212",
                               address="some address", userType="Instructor")
        self.user1.save()
        self.user1Account = User(username="john", email=self.user1.email, password="password123")
        self.user1Account.save()
        # user 2
        self.user2 = UserTable(firstName="Jeff", lastName="Doe", email="Jeff@gmail.com", phone="262-724-8212",
                               address="some address", userType="Instructor")
        self.user2.save()
        self.user2Account = User(username="jeff", email=self.user2.email, password="password123")
        self.user2Account.save()

    def test_deleteAccount(self):
        result = self.app.deleteAccount(self.user1Account.id, self.user1Account.id)
        self.assertEqual("Account deleted successfully", result)

    def test_deleteAccountInvalidAccount(self):
        result = self.app.deleteAccount(99999999, 99999999)
        self.assertEqual("Failed to delete account", result)

    def test_deleteAccountEmptyArguments(self):
        with self.assertRaises(ValueError):
            self.app.deleteAccount("", "")

    def test_deleteAccountEmptyUsername(self):
        with self.assertRaises(ValueError):
            self.app.deleteAccount("", self.user1.email)

    def test_deleteAccountEmptyEmail(self):
        with self.assertRaises(ValueError):
            self.app.deleteAccount(self.user1Account.username, "")

    def test_deleteAccountWrongEmail(self):
        result = self.app.deleteAccount(self.user1Account.id, self.user2Account.id)
        self.assertEqual("username/email match error", result)

    def test_deleteTwoAccount(self):
        result = self.app.deleteAccount(self.user1Account.id, self.user1Account.id)
        result2 = self.app.deleteAccount(self.user2Account.id, self.user2Account.id)
        self.assertEqual("Account deleted successfully", result, result2)

    def test_invalidArg(self):
        result = self.app.deleteAccount(1, "ID")
        self.assertEqual("username/email match error", result)

    def test_deleteSameAccountTwice(self):
        result = self.app.deleteAccount(self.user1Account.id, self.user1Account.id)
        result2 = self.app.deleteAccount(self.user1Account.id, self.user1Account.id)
        self.assertEqual("Failed to delete account", result2)