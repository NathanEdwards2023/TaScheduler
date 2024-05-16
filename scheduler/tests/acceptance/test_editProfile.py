import unittest

from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from ProfilePage import ProfilePage
from scheduler.views import profile, AdminAccManagement
from scheduler.models import UserTable


class TestEditAccountProfileAcceptance(TestCase):
    def setUp(self):
        self.profile = ProfilePage()
        self.user1 = UserTable(firstName="adminTest", lastName="adminTest", email="adminTest@gmail.com",
                               phone="adminTest", address="adminTest", userType="admin")
        self.user1.save()
        self.user1Account = User.objects.create_user(username="adminTest", password="adpassword",
                                                     email=self.user1.email)
        self.user1Account.save()

        self.user2 = UserTable(firstName="Other", lastName="Guy", email="otherGuy@gmail.com",
                               phone="000-000-0000", address="0000 Zeroth street", userType="ta")
        self.user2.save()
        self.user2Account = User.objects.create_user(username="OtherGuy", password="OtherGuysPassword",
                                                     email=self.user2.email)
        self.user2Account.save()

    def tearDown(self):
        self.user1.delete()
        self.user1Account.delete()
        self.user2.delete()
        self.user2Account.delete()

    def test_edit_profile_success(self):
        self.client.login(username=self.user1Account.username, password="adpassword")

        response = self.client.get(reverse('profile'), follow=True)
        self.assertEqual(response.status_code, 200)

        data = {
            "userEmail": self.user1.email,
            "editAccountFirstName": "Admin",
            "editAccountLastName": "Test",
            "editAccountEmail": "testAdmin@yahoo.com",
            "editAccountPhoneNumber": "987-654-TEST",
            "editAccountAddress": "1243 Test St",
            "editAccountSkills": "Python, Java",
            "editProfileButton": "Submit",
        }

        response = self.client.post(reverse("profile"), data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify that the email has been updated
        self.assertTrue(User.objects.filter(email='testAdmin@yahoo.com').exists())
        self.assertTrue(UserTable.objects.filter(email='testAdmin@yahoo.com').exists())
        updated_user = UserTable.objects.get(email='testAdmin@yahoo.com')
        self.assertEqual(updated_user.firstName, "Admin")
        self.assertEqual(updated_user.lastName, "Test")
        self.assertEqual(updated_user.phone, "987-654-TEST")
        self.assertEqual(updated_user.address, "1243 Test St")
        self.assertEqual(updated_user.skills, "Python, Java")

    def test_edit_profile_failure(self):
        self.client.login(username=self.user1Account.username, password="adpassword")

        response = self.client.get(reverse('profile'), follow=True)
        self.assertEqual(response.status_code, 200)

        data = {
            "userEmail": self.user1.email,
            "editAccountFirstName": "Admin",
            "editAccountLastName": "Test",
            "editAccountEmail": self.user2.email,  # Use self.user2.email, which already exists
            "editAccountPhoneNumber": "987-654-TEST",
            "editAccountAddress": "1243 Test St",
            "editAccountSkills": "Python, Java",
            "editProfileButton": "Submit",
        }

        response = self.client.post(reverse("profile"), data, follow=True)
        self.assertEqual(response.status_code, 200)

        updated_user = UserTable.objects.get(email=self.user1.email)
        self.assertNotEqual(updated_user.email, self.user2.email)

