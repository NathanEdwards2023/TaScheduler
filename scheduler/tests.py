import unittest

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse

import scheduler.views
from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable, CourseTable, LabTable, UserCourseJoinTable, SectionTable
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
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
        UserTable.objects.all().delete()
        self.user1 = UserTable(firstName="instructor", lastName="instructor", email="instruct@gmail.com",
                               phone="262-555-5555",
                               address="some address", userType="instructor")
        self.user1.save()

    def tearDown(self):
        # Clean up test data
        CourseTable.objects.all().delete()
        UserTable.objects.all().delete()
        self.user1.delete()

    def test_createCourse_correctly(self):
        self.app.createCourse("Course1", "")
        course = CourseTable.objects.get(courseName="Course1")
        self.assertIsNotNone(course)

    def test_createCourse_duplicateName(self):
        self.app.createCourse("Course1", "")
        with self.assertRaises(ValueError):
            self.app.createCourse("Course1", "")
        self.assertEqual(CourseTable.objects.filter(courseName="Course1").count(), 1)

    def test_createCourse_emptyCourseName(self):
        with self.assertRaises(ValueError):
            self.app.createCourse("", "")

    def test_createCourse_withInstructor(self):
        self.app.createCourse("Course1", self.user1.id)
        course = CourseTable.objects.get(courseName="Course1")
        self.assertIsNotNone(course)


class TestCreateCourseAcc(TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.user1 = UserTable(firstName="adminTest", lastName="adminTest", email="adminTest@gmail.com",
                               phone="adminTest",
                               address="adminTest", userType="admin")
        self.user1.save()
        self.user1Account = User(username="adminTest", password="adpassword", email=self.user1.email)
        self.user1Account.save()

        self.user2 = UserTable(firstName="Jeff", lastName="Thompson", email="nonadmin@gmail.com",
                               phone="5484651456",
                               address="123 street", userType="instructor")
        self.user2.save()
        self.userAccount2 = User(username="JeffT", password="password123", email=self.user2.email)
        self.userAccount2.save()

    def tearDown(self):
        # Clean up test data
        self.user1.delete()
        self.user1Account.delete()
        self.user2.delete()
        self.userAccount2.delete()

    def test_courseCourse_page(self):
        # Ensure that the course creation form is rendered correctly
        request = RequestFactory().get(reverse('courseManagement'))
        request.user = self.user1Account

        response = scheduler.views.courseManagement(request)

        self.assertEqual(response.status_code, 200)

    def test_courseManagement_redirect_non_admin(self):
        # Ensure that non-admin users are redirected to the home page when trying to access courseManagement
        request = RequestFactory().get(reverse('courseManagement'))
        request.user = self.userAccount2

        response = scheduler.views.courseManagement(request)

        self.assertEqual(response.status_code, 302)  # redirects

    def test_course_creation(self):
        self.client.login(username="adminTest", password="adpassword")
        # Ensure that a course can be created
        data = {
            'courseName': "New Course",
            'instructorSelect': self.user2.id,
            'createCourseBtn': 'Submit',  # button used
        }
        print(data)
        response = self.client.post(reverse('courseManagement'), data)
        self.assertEqual(response.status_code, 302)  # redirects to self
        newCourse = CourseTable.objects.get(courseName="New Course")
        print(newCourse)
        self.assertTrue(CourseTable.objects.filter(courseName='New Course').exists())
        self.assertTrue(UserCourseJoinTable.objects.filter(courseId=newCourse, userId=self.user2).exists())

    def test_invalid_course_creation(self):
        # Ensure that an invalid course cannot be created
        data = {
            'courseName': '',  # Invalid empty course name
            'instructorSelect': "",
        }
        response = self.client.post(reverse('courseManagement'), data)
        self.assertEqual(response.status_code, 302)  # redirects to self
        self.assertFalse(CourseTable.objects.filter(courseName='').exists())


class TestEditCourse(unittest.TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.user1 = UserTable(firstName="Rory", lastName="Christlieb", email="RoryC@gmail.com", phone="123-455-5555",
                               address="some address", userType="instructor")
        self.user1.save()
        self.user1Account = User(username="RoryC", password="password", email=self.user1.email)
        self.user1Account.save()

        self.user2 = UserTable(firstName="Matt", lastName="Kretsch", email="RoryC@gmail.com", phone="123-455-5555",
                               address="some address", userType="instructor")
        self.user2.save()
        self.user2Account = User(username="MattK", password="password", email=self.user1.email)
        self.user2Account.save()

        self.course1 = CourseTable(courseName="Computer Science 361", instructorId=self.user1.id,
                                   time="MoWeFr 2:00pm-3:00pm")

    def tearDown(self):
        self.user1.delete()
        self.user1Account.delete()
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

    def test_editCourse_invalidInstructor(self):
        with self.assertRaises(ValueError):
            self.app.editCourse(self.course1.id, 'Computer Science 362', 999, 'TuTh 2:30pm - 3:30pm')

    def test_editCourse_noActualChanges(self):
        with self.assertRaises(Exception) as context:
            self.app.editCourse(self.course1.id, 'Computer Science 361', self.user1.id, 'MoWeFr 2:00pm-3:00pm')
            self.assertIn("No changes were made", str(context.exception))


class TestCreateAccount(unittest.TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()

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
        self.app.createAccount('user', 'testuser@example.com', 'password')
        with self.assertRaises(Exception) as context:
            self.app.createAccount('user', 'testuser@example.com', 'password')
            self.assertIn("User already exists", str(context.exception))


class CreateAccountTestCase(TestCase):
    def setUp(self):
        self.createAccount_url = reverse('createAccount')
        self.home_url = reverse('login')
        self.login_url = reverse('login')

    def tearDown(self):
        User.objects.filter(username='testuser', email='test@user.com').delete()
        UserTable.objects.filter(email='test@user.com').delete()

    def test_createAccount_success(self):
        response = self.client.post(self.createAccount_url,
                                    {'username': 'testuser', 'email': 'test@user.com', 'password': 'password'},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='testuser', email='test@user.com').exists())
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'password'}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, expected_url=reverse('home'))

    def test_createAccount_failure(self):
        with self.assertRaises(ValueError) as context:
            self.client.post(self.createAccount_url,
                             {'username': '', 'email': 'nonExister@test.com', 'password': 'wordToPass'},
                             follow=True)
        self.assertEqual(str(context.exception), "All fields need to be filled out")
        self.assertFalse(User.objects.filter(username='', email='nonExister@test.com').exists())
        response = self.client.post(self.login_url, {'username': '', 'password': 'wordToPass'}, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)


class TestEditAccount(TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        user = UserTable(firstName="John", lastName="Doe", email="email@gmail.com", phone="262-724-8212",
                         address="some address", userType="instructor")
        user.save()
        userAccount = User(username="johnD", password="password123", userId=user.email)
        userAccount.save()

    def test_editAccount(self):
        newUser = self.app.editAccount(0, "newemail@uwm.com", "1234567890", "123 street", "TA")
        self.assertEqual(newUser,
                         UserTable(firstName="John", lastName="Doe", email="newemail@uwm.com", phone="1234567890",
                                   address="123 street", role="TA"))

    def test_editMissingAccount(self):
        self.assertRaises(ValueError,
                          self.app.editAccount(5, "newemail@uwm.com", "1234567890", "123 street", "TA"))


class TestDeleteAccount(TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        # user 1
        self.user1 = UserTable(firstName="John", lastName="Doe", email="John@gmail.com", phone="262-724-8212",
                               address="some address", userType="instructor")
        self.user1.save()
        self.user1Account = User(username="john", email=self.user1.email, password="password123")
        self.user1Account.save()
        # user 2
        self.user2 = UserTable(firstName="Jeff", lastName="Doe", email="Jeff@gmail.com", phone="262-724-8212",
                               address="some address", userType="instructor")
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

        self.assertContains(response, 'Account deleted successfully')

    def test_adminAccManagement_DeleteNotExist(self):
        request = RequestFactory().post(reverse('adminAccManagement'))
        request.user = self.user1Account
        for userID in range(1, 9999):
            try:
                User.objects.get(id=userID)
            except User.DoesNotExist:
                requestCopy = request.POST.copy()
                requestCopy['deleteAccountName'] = userID  # Provide username to delete
                requestCopy['deleteAccountEmail'] = userID  # Provide email to delete
                requestCopy['deleteAccBtn'] = 'Delete'  # Simulate button click

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


class TestCreateSection(unittest.TestCase):
    def setUp(self):
        self.app = AdminAssignmentPage()
        self.user1 = UserTable(firstName="matt", lastName="matt", email="matt@gmail.com", phone="262-555-5555",
                               address="some address", userType="instructor")
        self.user1.save()
        self.user1Account = User(username="matt", password="e121dfa91w", email=self.user1.email)
        self.user1Account.save()

        self.course1 = CourseTable(courseName="unitTest")
        self.course1.save()
        self.joinTable = UserCourseJoinTable(courseId=self.course1, userId=self.user1)
        self.joinTable.save()

    def tearDown(self):
        # Clean up test data
        self.user1.delete()
        self.user1Account.delete()
        self.course1.delete()
        self.joinTable.delete()

    def test_createSection_correctly(self):
        self.app.createSection("SectionUnitTest1", self.joinTable.id)
        section = SectionTable.objects.filter(name="SectionUnitTest1").first()

        self.assertEqual((section.name, section.userCourseJoinId.id), ("SectionUnitTest1", self.joinTable.id))

    def test_createSection_noJoinTable(self):
        # returns true if invalid Join table ID
        for joinTableID in range(1, 9999):
            try:
                UserCourseJoinTable.objects.get(id=joinTableID)
            except User.DoesNotExist:
                with self.assertRaises(ValueError):
                    self.app.createSection("SectionUnitTest1", joinTableID)

    def test_createSection_emptySectionName(self):
        with self.assertRaises(ValueError):
            self.app.createSection("", self.joinTable.id)

class AssignTAToCourseTestCase(TestCase):
    def setUp(self):
        # Creating user and admin instances
        self.admin_user = User.objects.create_user(username='admin', password='admin123', is_staff=True)
        self.ta_user = UserTable.objects.create(firstName="John", lastName="Doe", email="johndoe@example.com", userType="TA")
        self.course = CourseTable.objects.create(courseName="Introduction to Python")

        # Log in the admin user
        self.client.login(username='admin', password='admin123')

    def test_successful_ta_assignment(self):
        # Posting data to simulate form submission
        response = self.client.post(reverse('courseManagement'), {
            'assignTAToCourseBtn': True,
            'courseId': self.course.id,
            'userId': self.ta_user.id  # Adjusted to use 'userId'
        }, follow=True)

        # Check if the response indicates a successful assignment
        self.assertRedirects(response, reverse('courseManagement'))  # Assuming it redirects back to the course management page
        self.assertTrue(UserCourseJoinTable.objects.filter(courseId=self.course, userId=self.ta_user).exists())
        messages = list(response.context['messages'])
        self.assertIn("TA successfully assigned to course.", str(messages[0]))

    def test_invalid_user_id(self):
        # Testing with an invalid user ID
        response = self.client.post(reverse('courseManagement'), {
            'assignTAToCourseBtn': True,
            'courseId': self.course.id,
            'userId': 9999  # Non-existent user ID
        }, follow=True)

        # Check that the assignment was not made
        self.assertFalse(UserCourseJoinTable.objects.filter(courseId=self.course, userId=9999).exists())
        messages = list(response.context['messages'])
        self.assertIn("Selected TA not found.", str(messages[0]))

    def test_non_admin_access(self):
        # Non-admin user (e.g., an instructor) attempts to assign a TA
        non_admin_user = User.objects.create_user(username='instructor', password='password123')
        self.client.login(username='instructor', password='password123')
        response = self.client.post(reverse('courseManagement'), {
            'assignTAToCourseBtn': True,
            'courseId': self.course.id,
            'userId': self.ta_user.id
        }, follow=True)

        # Expect a redirect to a permission denied page or home
        self.assertRedirects(response, reverse('home'))  # Redirect to home for non-admin


class AssignTAToLabTestCase(TestCase):
    def setUp(self):
        # Create users
        self.admin_user = User.objects.create_user(username='admin', password='admin123', is_staff=True)
        self.ta_user = UserTable.objects.create(firstName="John", lastName="Doe", email="johndoe@example.com",
                                                userType="TA")

        # Create course and section
        self.course = CourseTable.objects.create(courseName="Introduction to Python")
        self.section = SectionTable.objects.create(name="Section 1")
        self.lab = LabTable.objects.create(sectionNumber="Lab 1", sectionId=self.section)

        self.client = Client()

    def test_successful_ta_assignment_to_lab(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('assignTAToLab'), {
            'labId': self.lab.id,
            'userId': self.ta_user.id
        })
        self.assertContains(response, "TA successfully assigned to lab.")
        self.assertEqual(LabTable.objects.filter(taId=self.ta_user.id).count(), 1)

    def test_invalid_ta_id(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('assignTAToLab'), {
            'labId': self.lab.id,
            'userId': 9999  # Non-existing TA ID
        })
        self.assertContains(response, "Selected TA not found.")

    def test_invalid_lab_id(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.post(reverse('assignTAToLab'), {
            'labId': 9999,  # Non-existing Lab ID
            'userId': self.ta_user.id
        })
        self.assertContains(response, "Selected lab not found.")

    def test_non_admin_access(self):
        non_admin_user = User.objects.create_user(username='nonadmin', password='password123')
        self.client.login(username='nonadmin', password='password123')
        response = self.client.post(reverse('assignTAToLab'), {
            'labId': self.lab.id,
            'userId': self.ta_user.id
        })
        self.assertRedirects(response, reverse('home'))  # Redirect to home or login

    def test_unauthenticated_access(self):
        response = self.client.post(reverse('assignTAToLab'), {
            'labId': self.lab.id,
            'userId': self.ta_user.id
        })
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('assignTAToLab')}")

    def tearDown(self):
        self.admin_user.delete()
        self.ta_user.delete()
        self.course.delete()
        self.section.delete()
        self.lab.delete()




if __name__ == '__main__':
    unittest.main()
