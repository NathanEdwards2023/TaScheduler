import unittest

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable


class TestEditAccountProfileAcceptance(TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.user1 = UserTable(firstName="adminTest", lastName="adminTest", email="adminTest@gmail.com",
                               phone="adminTest",
                               address="adminTest", userType="admin")
        self.user1.save()
        self.user1Account = User(username="adminTest", password="adpassword", email=self.user1.email)
        self.user1Account.save()

        self.user2 = UserTable(firstName="deleteTest", lastName="deleteTest", email="deleteTest@gmail.com",
                               phone="deleteTest",
                               address="deleteTest", userType="ta")
        self.user2.save()
        self.user2Account = User(username="deleteTest", password="delpassword", email=self.user2.email)
        self.user2Account.save()

    def tearDown(self):
        self.user1.delete()
        self.user1Account.delete()
        self.user2.delete()
        self.user2Account.delete()

    def test_edit_account_success(self):
        data = {
            "editAccountEmail": "newemail@uwm.com",
            "editAccountPhoneNumber": "9876543210",
            "editAccountAddress": "456 Elm St",
            "editAccountSkills": "Python, Java",
        }
        response = self.client.post(reverse("profile"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        updated_user = UserTable.objects.get(email="newemail@uwm.com")
        self.assertEqual(updated_user.phone, "9876543210")
        self.assertEqual(updated_user.address, "456 Elm St")
        self.assertEqual(updated_user.userType, "ta")

    def test_edit_account_failure(self):
        data = {
            "editAccountEmail": "invalidemail",
            "editAccountPhoneNumber": "invalidphone",
            "editAccountAddress": "",
            "editAccountSkills": "Python, Java",
        }
        response = self.client.post(reverse("profile"), data, follow=True)
        self.assertEqual(response.status_code, 200)
        updated_user = UserTable.objects.get(email="john@example.com")
        self.assertEqual(updated_user.phone, "1234567890")
        self.assertEqual(updated_user.address, "123 Main St")
        self.assertEqual(updated_user.userType, "instructor")
