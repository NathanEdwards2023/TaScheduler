import unittest

from django.contrib.auth.models import User

from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable


class TestCreateAccount(unittest.TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.user1 = UserTable(firstName="Rory", lastName="Christlieb", email="RoryC@gmail.com", phone="123-455-5555",
                               address="some address", userType="admin")
        self.user1.save()
        self.user1Account = User(username="RoryC", password="password", email=self.user1.email)
        self.user1Account.save()
        self.user2 = UserTable(firstName="John", lastName="Doe", email="JDoe@gmail.com", phone="123-456-7890",
                               address="another address", userType="instructor")
        self.user2.save()
        self.user2Account = User(username="John_Doe", password="anonymous", email=self.user2.email)
        self.user2Account.save()

    def tearDown(self):
        self.user1.delete()
        self.user1Account.delete()
        self.user2.delete()
        self.user2Account.delete()

    def test_createAccountSuccess(self):
        result = self.app.createAccount('user', 'testuser@example.com', 'password')
        self.assertTrue(result)

    def test_createAccountEmptyUsername(self):
        with self.assertRaises(ValueError):
            self.app.createAccount('', 'testuser@example.com', 'password')

    def test_createAccountWithWeakPassword(self):
        with self.assertRaises(ValueError):
            self.app.createAccount('user', 'testuser@example.com', 'pass')

    def test_createAccountWithInvalidEmail(self):
        with self.assertRaises(ValueError):
            self.app.createAccount('user', 'not-an-email', 'password')

    def test_createAccountWithExistingUser(self):
        with self.assertRaises(ValueError):
            self.app.createAccount('user', 'testuser@example.com', 'password')
            self.app.createAccount('user', 'testuser@example.com', 'password')


if __name__ == '__main__':
    unittest.main()
