import unittest

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User

from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable
from django.test import TestCase
from django.urls import reverse

from scheduler.views import AdminAccManagement


class CreateAccountTestCase(TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.user1Account = User(username="RoryC", password="password", email="RoryC@gmail.com")
        self.user1Account.save()
        self.user1 = UserTable(firstName="Rory", lastName="Christlieb", email=self.user1Account.email,
                               phone="123-455-5555",
                               address="some address", userType="admin")
        self.user1.save()
        self.user1.save()
        self.user2Account = User(username="John_Doe", password="anonymous", email="JDoe@gmail.com")
        self.user2Account.save()
        self.user2 = UserTable(firstName="John", lastName="Doe", email=self.user2Account.email, phone="123-456-7890",
                               address="another address", userType="instructor")
        self.user2.save()
        self.createAccount_url = reverse('createAccount')
        self.home_url = reverse('login')
        self.login_url = reverse('login')

    def tearDown(self):
        User.objects.filter(username='testuser', email='test@user.com').delete()
        UserTable.objects.filter(email='test@user.com').delete()

    def test_createAccount_page(self):
        request = RequestFactory().get(reverse('adminAccManagement'))
        request.user = self.user1Account
        response = AdminAccManagement.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_createAccount_redirect_non_admin(self):
        request = RequestFactory().get(reverse('adminAccManagement'))
        request.user = self.user2Account
        response = AdminAccManagement.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_createAccount_success(self):
        request = RequestFactory().get(reverse('adminAccManagement'))
        request.user = self.user1Account
        response = AdminAccManagement.as_view()(request)
        self.assertEqual(response.status_code, 200)
        data = {
            'createAccountName': 'testuser',
            'createAccountEmail': 'test@user.com',
            'createAccountPassword': 'password',
            'createAccBtn': 'Submit',
        }
        self.client.post(reverse('adminAccManagement'), data, follow=True)
        self.assertTrue(User.objects.filter(username='testuser', email='test@user.com').exists())
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'password'}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, expected_url=reverse('home'))

    def test_createAccount_failure(self):
        request = RequestFactory().get(reverse('adminAccManagement'))
        request.user = self.user1Account
        response = AdminAccManagement.as_view()(request)
        self.assertEqual(response.status_code, 200)
        data = {
            'username': '',
            'email': 'nonExister@test.com',
            'password': 'wordToPass',
            'createAccountBtn': 'Submit',
        }
        self.client.post(reverse('adminAccManagement'), data, follow=True)
        self.assertFalse(User.objects.filter(username='', email='nonExister@test.com').exists())
        response = self.client.post(self.login_url, {'username': '', 'password': 'wordToPass'}, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)


if __name__ == '__main__':
    unittest.main()