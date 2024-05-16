from django.test import TestCase
from unittest.mock import patch, MagicMock
from scheduler.models import CourseTable, UserTable, UserCourseJoinTable
from scheduler.adminAssignmentPage import AdminAssignmentPage

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

if __name__ == '__main__':
    unittest.main()
