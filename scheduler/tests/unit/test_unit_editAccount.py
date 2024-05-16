import unittest

from django.contrib.auth.models import User

from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable


class TestEditAccount(unittest.TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.user = UserTable(firstName="John", lastName="Doe", email="email@gmail.com", phone="262-724-8212",
                              address="some address", userType="instructor")
        self.user.save()
        self.userAccount = User(username="johnD", password="password123", email=self.user.email)
        self.userAccount.save()

    def tearDown(self):
        self.user.delete()
        self.userAccount.delete()

    def test_editAccount(self):
        newUser = self.app.editAccount(self.user.email, "newemail@uwm.com", "1234567890", "123 street", "TA")
        self.assertEqual(newUser.email, "newemail@uwm.com")
        self.assertEqual(newUser.phone, "1234567890")
        self.assertEqual(newUser.address, "123 street")
        self.assertEqual(newUser.userType, "TA")

    def test_editMissingAccount(self):
        self.assertRaises(ValueError, self.app.editAccount, "nonexistent@email.com", "newemail@uwm.com", "1234567890",
                          "123 street", "TA")


if __name__ == '__main__':
    unittest.main()
