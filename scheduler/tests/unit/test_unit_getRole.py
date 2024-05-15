import unittest
from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable


class TestGetRole(unittest.TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        # Create a test user for each test case
        self.ins = UserTable(firstName="Matt", lastName="Matt", email="insTest@gmail.com", phone="262-555-5555",
                             address="Some address", userType="instructor")
        self.ins.save()

        self.ta = UserTable(firstName="Matt", lastName="Matt", email="taTest@gmail.com", phone="262-555-5555",
                            address="Some address", userType="ta")
        self.ta.save()

        self.admin = UserTable(firstName="Matt", lastName="Matt", email="adminTest@gmail.com", phone="262-555-5555",
                               address="Some address", userType="admin")
        self.admin.save()

    def tearDown(self):
        # Clean up test data after each test case
        self.ins.delete()
        self.ta.delete()
        self.admin.delete()

    def test_getRole_instructor(self):
        # Test getting role for instructor
        role = self.app.getRole("insTest@gmail.com")
        self.assertEqual(role, "instructor")

    def test_getRole_ta(self):
        # Test getting role for ta
        role = self.app.getRole("taTest@gmail.com")
        self.assertEqual(role, "ta")

    def test_getRole_admin(self):
        # Test getting role for admin
        role = self.app.getRole("adminTest@gmail.com")
        self.assertEqual(role, "admin")

    def test_getRole_fakeUser(self):
        # Test getting role for user that does not exist
        role = self.app.getRole("randomEmail@something.com")
        self.assertIsNone(role)

    def test_getRole_noEmail(self):
        # Test getting role with no email
        role = self.app.getRole("")
        self.assertIsNone(role)


if __name__ == '__main__':
    unittest.main()
