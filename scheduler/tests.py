import unittest
from unittest.mock import MagicMock, patch

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse

import scheduler.views
from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable, CourseTable, LabTable, UserCourseJoinTable, SectionTable
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from scheduler.views import AdminAccManagement


# Acceptance Tests for Login
class LoginTestCase(TestCase):
    def setUp(self):
        user = get_user_model()
        self.user = user.objects.create_user(username='testuser', password='password')
        self.login_url = reverse('login')
        self.home_url = reverse('home')

    def test_login_success(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'password'}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, expected_url=reverse('home'))

    def test_login_failure(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'wrong'}, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertContains(response, "Please enter a correct username and password.")

    def test_login_redirect_to_home(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'password'}, follow=True)
        self.assertRedirects(response, self.home_url, status_code=302, target_status_code=200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_logout(self):
        self.client.login(username='testuser', password='password')
        logout_url = reverse('logout')
        response = self.client.get(logout_url, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertRedirects(response, expected_url=reverse('login'))


class TestCreateCourse(unittest.TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.user1 = UserTable(firstName="matt", lastName="matt", email="matt@gmail.com", phone="262-555-5555",
                               address="some address", userType="instructor")
        self.user1.save()
        self.user1Account = User(username="matt", password="e121dfa91w", email=self.user1.email)
        self.user1Account.save()

    def tearDown(self):
        # Clean up test data
        self.user1.delete()
        self.user1Account.delete()

    def test_createCourse_correctly(self):
        self.app.createCourse("Course1", self.user1.id)
        course = CourseTable.objects.filter(courseName="Course1").first()

        self.assertEqual((course.courseName, course.instructorId.id), ("Course1", self.user1.id))

    def test_createCourse_duplicateName(self):
        self.app.createCourse("Course1", self.user1.id)
        with self.assertRaises(ValueError):
            self.app.createCourse("Course1", self.user1.id)
        self.assertEqual(CourseTable.objects.filter(courseName="Course1").count(), 1)

    def test_createCourse_noInstructor(self):
        # returns true if invalid instructor ID
        with self.assertRaises(ValueError):
            self.app.createCourse("Course10", 10)

    def test_createCourse_emptyCourseName(self):
        with self.assertRaises(ValueError):
            self.app.createCourse("", self.user1.id)


class TestCreateCourseAcc(TestCase):
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

        user2 = UserTable(firstName="Jeff", lastName="Thompson", email="nonadmin@gmail.com", phone="5484651456",
                          address="123 street", userType="instructor")
        user2.save()
        userAccount2 = User(username="JeffT", password="password123", email=user2.email)
        userAccount2.save()

    def tearDown(self):
        # Clean up test data
        self.user1.delete()
        self.user1Account.delete()
        self.user2.delete()
        self.user2Account.delete()

    def test_courseCourse_page(self):
        # Ensure that the course creation form is rendered correctly
        request = RequestFactory().get(reverse('courseManagement'))
        request.user = self.user1Account

        response = scheduler.views.courseManagement(request)

        self.assertEqual(response.status_code, 200)

    def test_courseManagement_redirect_non_admin(self):
        # Ensure that non-admin users are redirected to the home page when trying to access courseManagement
        request = RequestFactory().get(reverse('courseManagement'))
        request.user = self.user2Account

        response = scheduler.views.courseManagement(request)

        self.assertEqual(response.status_code, 302)  # redirects

    def test_course_creation(self):
        # Create a test instructor
        instructor = UserTable.objects.create(firstName="John", lastName="Doe", email="john@example.com",
                                              phone="1234567890", address="123 Main St", userType="instructor")
        self.client.login(username="adminTest", password="adpassword")
        # Ensure that a course can be created
        data = {
            'courseName': 'New Course',
            'instructorSelect': instructor.id,
            'createCourseBtn': 'Submit',  # button used

        }
        response = self.client.post(reverse('courseManagement'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CourseTable.objects.filter(courseName='New Course', instructorId=instructor).exists())

    def test_invalid_course_creation(self):
        # Ensure that an invalid course cannot be created
        data = {
            'courseName': '',  # Invalid empty course name
            'instructorSelect': 9999,  # Invalid instructor ID
        }
        response = self.client.post(reverse('courseManagement'), data)
        self.assertEqual(response.status_code, 302)  # redirects to self
        self.assertFalse(CourseTable.objects.filter(courseName='', instructorId=9999).exists())


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


class TestEditCourseAcceptance(TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.user1 = UserTable(firstName="Rory", lastName="Christlieb", email="RoCh@gmail.com", phone="123-455-5555",
                           address="some address", userType="admin")
        self.user1.save()
        self.user1Account = User(username="RoryC", password="password", email=self.user1.email)
        self.user1Account.save()
        self.user2 = UserTable(firstName="John", lastName="Doe", email="JDoe@gmail.com", phone="123-456-7890",
                           address="another address", userType="instructor")
        self.user2.save()
        self.user2Account = User(username="John_Doe", password="anonymous", email=self.user2.email)
        self.user2Account.save()

        self.course1 = CourseTable.objects.create(courseName="Computer Science 361", time="MoWeFr 2:00pm-3:00pm")
        self.courseManagement_url = reverse('courseManagement')
        self.home_url = reverse('home')
        self.login_url = reverse('login')

    def tearDown(self):
        self.user1.delete()
        self.user1Account.delete()
        self.user2.delete()
        self.user2Account.delete()
        self.course1.delete()

    def test_courseCourse_page(self):
        # Ensure that the course creation form is rendered correctly
        request = RequestFactory().get(self.courseManagement_url)
        request.user = self.user1Account
        response = scheduler.views.courseManagement(request)
        self.assertEqual(response.status_code, 200)

    def test_courseManagement_redirect_non_admin(self):
        request = RequestFactory().get(self.courseManagement_url)
        request.user = self.user2Account
        response = scheduler.views.courseManagement(request)
        self.assertEqual(response.status_code, 302)

    def test_course_edit_success(self):
        request = RequestFactory().get(self.courseManagement_url)
        request.user = self.user1Account
        response = AdminAccManagement.as_view()(request)
        self.assertEqual(response.status_code, 200)
        data = {
            'editCourseSelect': 1,
            'editName': 'Computer Science 362',
            'editTime': 'TuTh 2:30pm - 3:30pm',
            'editCourseBtn': 'Submit',
        }
        self.client.post(self.courseManagement_url, data, follow=True)
        self.assertTrue(CourseTable.objects.filter(courseName='Computer Science 362').exists())
        self.assertEqual(response.status_code, 200)

    def test_course_edit_failure(self):
        request = RequestFactory().get(reverse('courseManagement'))
        request.user = self.user1Account
        response = AdminAccManagement.as_view()(request)
        self.assertEqual(response.status_code, 200)
        data = {
            'editCourseSelect': 100000000000000,
            'editName': 'Computer Science 362',
            'editTime': 'TuTh 2:30pm - 3:30pm',
            'editCourseBtn': 'Submit',
        }
        response = self.client.post(reverse('courseManagement'), data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(CourseTable.objects.filter(courseName='').exists())


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
        self.assertRaises(ValueError, self.app.editAccount, "nonexistent@email.com", "newemail@uwm.com", "1234567890", "123 street", "TA")


class TestDeleteAccount(TestCase):
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


class TestDeleteAccountACCEPTANCE(TestCase):
    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)
        self.client = None

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
        # Clean up test data
        self.user1.delete()
        self.user1Account.delete()
        self.user2.delete()
        self.user2Account.delete()

    def test_adminAccManagement_Admin(self):
        request = RequestFactory().get(reverse('adminAccManagement'))  # Use reverse to get the URL
        request.user = self.user1Account

        response = AdminAccManagement.as_view()(request)

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

    def test_adminAccManagement_Ta(self):
        request = RequestFactory().get(reverse('adminAccManagement'))  # Use reverse to get the URL
        request.user = self.user2Account

        response = AdminAccManagement.as_view()(request)

        # Check if the response status code Redirect
        self.assertEqual(response.status_code, 302)

    def test_adminAccManagement_DeleteAccount(self):
        request = RequestFactory().post(reverse('adminAccManagement'))
        request.user = self.user1Account

        requestCopy = request.POST.copy()
        requestCopy['deleteAccountName'] = self.user2.id
        requestCopy['deleteAccountEmail'] = self.user2.id
        requestCopy['deleteAccBtn'] = 'Delete'

        request.POST = requestCopy

        response = AdminAccManagement.as_view()(request)

        self.assertContains(response, 'Failed to delete account')


class TestDeleteCourse(unittest.TestCase):
    def setUp(self):
        self.admin_page = AdminAssignmentPage()

        # Create a course
        self.course = CourseTable.objects.create(courseName="Test Course")

        # Create users
        self.user1 = UserTable.objects.create(email="user01@example.com")
        self.user2 = UserTable.objects.create(email="user02@example.com")

        # Create user-course associations
        self.user_course1 = UserCourseJoinTable.objects.create(courseId=self.course, userId=self.user1)
        self.user_course2 = UserCourseJoinTable.objects.create(courseId=self.course, userId=self.user2)

        # Create sections associated with the course
        self.section1 = SectionTable.objects.create(name="Section 1", userCourseJoinId=self.user_course1)
        self.section2 = SectionTable.objects.create(name="Section 2", userCourseJoinId=self.user_course2)

        # Create lab sections associated with the course
        self.lab1 = LabTable.objects.create(sectionNumber="Lab 001", sectionId=self.section1)
        self.lab2 = LabTable.objects.create(sectionNumber="Lab 002", sectionId=self.section2)

    def tearDown(self):
        # Clean up after each test by deleting created objects
        self.course.delete()
        self.lab1.delete()
        self.lab2.delete()
        self.user_course1.delete()
        self.user_course2.delete()
        self.user1.delete()
        self.user2.delete()

    def test_delete_course_success(self):
        result = self.admin_page.deleteCourse(id=self.course.id)
        self.assertTrue(result)

        # Verify that course and associated objects are deleted
        self.assertFalse(CourseTable.objects.filter(id=self.course.id).exists())
        self.assertFalse(UserCourseJoinTable.objects.filter(courseId=self.course).exists())
        self.assertFalse(SectionTable.objects.filter(name="Section 1").exists())
        self.assertFalse(SectionTable.objects.filter(name="Section 2").exists())

    def test_delete_course_not_found(self):
        result = self.admin_page.deleteCourse(id=999)
        self.assertFalse(result)

    def test_delete_course_with_no_labs(self):
        # Remove labs
        self.lab1.delete()
        self.lab2.delete()

        result = self.admin_page.deleteCourse(id=self.course.id)
        self.assertTrue(result)

        # Verify that course and associated objects are deleted
        self.assertFalse(CourseTable.objects.filter(id=self.course.id).exists())
        self.assertFalse(UserCourseJoinTable.objects.filter(courseId=self.course).exists())
        self.assertFalse(SectionTable.objects.filter(name="Section 1").exists())
        self.assertFalse(SectionTable.objects.filter(name="Section 2").exists())

    def test_delete_course_with_associated_objects_deleted(self):
        result = self.admin_page.deleteCourse(id=self.course.id)
        self.assertTrue(result)

        # Verify that users attached to the course are not deleted
        self.assertTrue(UserTable.objects.filter(id=self.user1.id).exists())
        self.assertTrue(UserTable.objects.filter(id=self.user2.id).exists())

        # Verify that associated lab sections are also deleted
        self.assertFalse(LabTable.objects.filter(sectionNumber="Lab 1").exists())
        self.assertFalse(LabTable.objects.filter(sectionNumber="Lab 2").exists())


class TestCreateLabSection(unittest.TestCase):
    def setUp(self):
        self.admin_page = AdminAssignmentPage()
        self.course = CourseTable.objects.create(courseName="Test Course")

    def tearDown(self):
        # Clean up the course created during testing
        self.course.delete()

    def test_create_lab_section_success(self):
        result = self.admin_page.createLabSection(courseId=self.course.id, sectionNumber="Lab #001")
        self.assertTrue(result)

        # Verify that lab section is created
        self.assertTrue(SectionTable.objects.filter(name="Lab #001", userCourseJoinId=self.course).exists())

    def test_create_lab_section_invalid_course(self):
        result, msg = self.admin_page.createLabSection(courseId=999, sectionNumber="Lab #001")
        self.assertFalse(result)
        self.assertEqual(msg, "Course does not exist")

    def test_create_lab_section_with_empty_name(self):
        with self.assertRaises(ValueError):
            self.admin_page.createLabSection(courseId=self.course.id, sectionNumber="")

    def test_create_lab_section_with_existing_name(self):
        # Create a lab section with the same name to emulate it already exists
        user = UserTable.objects.create(email="emailer@email.com", firstName="firstName", lastName="lastName")
        joinentry = UserCourseJoinTable.objects.create(courseId=self.course.id, userId=user)
        SectionTable.objects.create(name="Lab #001", userCourseJoinId=joinentry)

        #result, msg = self.admin_page.createLabSection(courseId=self.course, sectionNumber="Lab #001")
        #self.assertFalse(result)
        #self.assertEqual(msg, "Lab section already exists for this course")
        with self.assertRaises(ValueError):
            self.admin_page.createLabSection(courseId=self.course.id, sectionNumber="Lab #001")
        joinentry.delete()
        user.delete()

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


class AssignTAToCourseTestCase(TestCase):

    def setUp(self):
        self.admin_page = AdminAssignmentPage()
        self.course_id = 1
        self.user_id = 2
        self.mock_course = MagicMock(spec=CourseTable)
        self.mock_ta = MagicMock(spec=UserTable)

    @patch('scheduler.models.CourseTable.objects.get')
    @patch('scheduler.models.UserTable.objects.get')
    @patch('scheduler.models.UserCourseJoinTable.objects.update_or_create')
    def test_assign_ta_to_course_success(self, mock_update_or_create, mock_user_get, mock_course_get):
        mock_course_get.return_value = self.mock_course
        mock_user_get.return_value = self.mock_ta
        mock_update_or_create.return_value = (MagicMock(), True)

        success, message = self.admin_page.assignTAToCourse(self.course_id, self.user_id)
        self.assertTrue(success)
        self.assertEqual(message, "TA successfully assigned to course.")

    @patch('scheduler.models.CourseTable.objects.get')
    def test_course_not_found(self, mock_course_get):
        mock_course_get.side_effect = CourseTable.DoesNotExist

        success, message = self.admin_page.assignTAToCourse(self.course_id, self.user_id)
        self.assertFalse(success)
        self.assertEqual(message, "Course not found.")

    @patch('scheduler.models.CourseTable.objects.get')
    @patch('scheduler.models.UserTable.objects.get')
    def test_ta_not_found(self, mock_user_get, mock_course_get):
        mock_course_get.return_value = self.mock_course
        mock_user_get.side_effect = UserTable.DoesNotExist

        success, message = self.admin_page.assignTAToCourse(self.course_id, self.user_id)
        self.assertFalse(success)
        self.assertEqual(message, "TA not found or not eligible.")

    @patch('scheduler.models.CourseTable.objects.get')
    @patch('scheduler.models.UserTable.objects.get')
    @patch('scheduler.models.UserCourseJoinTable.objects.update_or_create')
    def test_ta_already_assigned(self, mock_update_or_create, mock_user_get, mock_course_get):
        mock_course_get.return_value = self.mock_course
        mock_user_get.return_value = self.mock_ta
        mock_update_or_create.return_value = (MagicMock(), False)

        success, message = self.admin_page.assignTAToCourse(self.course_id, self.user_id)
        self.assertFalse(success)
        self.assertEqual(message, "TA assignment updated but already existed.")

    @patch('scheduler.models.CourseTable.objects.get')
    @patch('scheduler.models.UserTable.objects.get')
    @patch('scheduler.models.UserCourseJoinTable.objects.update_or_create')
    def test_unexpected_error(self, mock_update_or_create, mock_user_get, mock_course_get):
        mock_course_get.return_value = self.mock_course
        mock_user_get.return_value = self.mock_ta
        mock_update_or_create.side_effect = Exception("Unexpected Error")

        success, message = self.admin_page.assignTAToCourse(self.course_id, self.user_id)
        self.assertFalse(success)
        self.assertEqual(message, "An error occurred: Unexpected Error")


class TestAssignTAToLab(TestCase):
    def setUp(self):
        self.admin_page = AdminAssignmentPage()
        self.lab_id = 1
        self.user_id = 1
        self.mock_lab = MagicMock(spec=LabTable)
        self.mock_ta = MagicMock(spec=UserTable)
        self.mock_section = MagicMock(spec=SectionTable)
        self.mock_lab.section_id = self.mock_section.id

    @patch('scheduler.models.LabTable.objects.get')
    @patch('scheduler.models.UserTable.objects.get')
    @patch('scheduler.models.SectionTable.objects.get')
    @patch('scheduler.models.UserLabJoinTable.objects.update_or_create')
    @patch('scheduler.models.UserSectionJoinTable.objects.update_or_create')
    def test_assign_tatolab_success(self, mock_section_update_or_create, mock_lab_update_or_create, mock_section_get, mock_user_get, mock_lab_get):
        mock_lab_get.return_value = self.mock_lab
        mock_user_get.return_value = self.mock_ta
        mock_section_get.return_value = self.mock_section
        mock_lab_update_or_create.return_value = (MagicMock(), True)
        mock_section_update_or_create.return_value = (MagicMock(), True)

        success, message = self.admin_page.assignTAToLab(self.lab_id, self.user_id)
        self.assertTrue(success)
        self.assertEqual(message, "TA successfully assigned to lab and corresponding section.")

    @patch('scheduler.models.LabTable.objects.get')
    def test_lab_not_found(self, mock_lab_get):
        mock_lab_get.side_effect = LabTable.DoesNotExist

        success, message = self.admin_page.assignTAToLab(self.lab_id, self.user_id)
        self.assertFalse(success)
        self.assertEqual(message, "Lab not found.")

    @patch('scheduler.models.LabTable.objects.get')
    @patch('scheduler.models.UserTable.objects.get')
    def test_ta_not_found(self, mock_user_get, mock_lab_get):
        mock_lab_get.return_value = MagicMock()  # Assume lab is found
        mock_user_get.side_effect = UserTable.DoesNotExist  # TA is not found

        success, message = self.admin_page.assignTAToLab(self.lab_id, self.user_id)
        self.assertFalse(success)
        self.assertEqual(message, "TA not found or not eligible.")

    @patch('scheduler.models.LabTable.objects.get')
    @patch('scheduler.models.UserTable.objects.get')
    @patch('scheduler.models.SectionTable.objects.get')
    def test_section_not_found(self, mock_section_get, mock_user_get, mock_lab_get):
        mock_lab_get.return_value = MagicMock()  # Assume lab is found
        mock_user_get.return_value = MagicMock()  # Assume TA is found
        mock_section_get.side_effect = SectionTable.DoesNotExist  # Section is not found

        success, message = self.admin_page.assignTAToLab(self.lab_id, self.user_id)
        self.assertFalse(success)
        self.assertEqual(message, "Section not found linked to the lab.")



if __name__ == '__main__':
    unittest.main()
