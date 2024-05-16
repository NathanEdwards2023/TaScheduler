from django.test import TestCase
from django.contrib.auth.models import User

from ProfilePage import ProfilePage
from scheduler.models import UserTable, CourseTable, UserCourseJoinTable  # Import from the models.py file
from adminAssignmentPage import AdminAssignmentPage  # Import from the adminAssignmentPage.py file


class TestEditProfile(TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.profile = ProfilePage()
        self.user1 = UserTable(firstName="John", lastName="Doe", email="email@gmail.com", phone="262-724-8212",
                               address="some address", skills="Python, Java", userType="instructor")
        self.user1.save()
        self.user1Account = User(username="johnD", password="password123", email=self.user1.email)
        self.user1Account.save()
        self.user2 = UserTable(firstName="Poor", lastName="Tom", email="poor@tom.com", phone="934-564-4569",
                               address="some address", skills="C++, JavaScript", userType="instructor")
        self.user2.save()
        self.user2Account = User(username="PoorTom", password="word_to_pass", email=self.user2.email)
        self.user2Account.save()

    def tearDown(self):
        self.user1.delete()
        self.user1Account.delete()
        self.user2.delete()
        self.user2Account.delete()

    def test_editAccount(self):
        new_user = self.profile.editProfile(self.user1.email, "John", "Doe", "newemail@uwm.com", "1234567890", "123 street", "Java, Python")
        self.assertEqual(new_user.firstName, "John")
        self.assertEqual(new_user.lastName, "Doe")
        self.assertEqual(new_user.email, "newemail@uwm.com")
        self.assertEqual(new_user.phone, "1234567890")
        self.assertEqual(new_user.address, "123 street")
        self.assertEqual(new_user.skills, "Java, Python")

    def test_editMissingAccount(self):
        with self.assertRaises(ValueError) as context:
            self.profile.editProfile("", "John", "Doe", "newemail@uwm.com", "1234567890", "123 street", "Java, Python")

    def test_editAccountEmailInUse(self):
        with self.assertRaises(ValueError) as context:
            self.profile.editProfile(self.user1.email, "John", "Doe", self.user2.email, "1234567890", "123 street", "Java, Python")

