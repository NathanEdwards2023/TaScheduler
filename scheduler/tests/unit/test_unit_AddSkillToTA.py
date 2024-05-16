from django.test import TestCase
from unittest.mock import patch, MagicMock
from scheduler.models import UserTable
from scheduler.adminAssignmentPage import AdminAssignmentPage

class TestAddSkillToTA(TestCase):
    def setUp(self):
        # Initialize AdminAssignmentPage for the tests
        self.ta_id = 1
        self.skill = "Python"
        self.mock_ta = MagicMock()
        self.mock_ta.skills = ""

    @patch('scheduler.models.UserTable.objects.get')
    def test_add_skill_successfully(self, mock_get):
        mock_get.return_value = self.mock_ta

        success, message = AdminAssignmentPage.add_skill_to_ta(self.ta_id, self.skill)

        self.assertTrue(success)
        self.assertEqual(message, "Skill successfully added.")
        self.mock_ta.save.assert_called_once()
        self.assertEqual(self.mock_ta.skills, "Python")

    @patch('scheduler.models.UserTable.objects.get')
    def test_add_skill_empty_skill(self, mock_get):
        success, message = AdminAssignmentPage.add_skill_to_ta(self.ta_id, "")

        self.assertFalse(success)
        self.assertEqual(message, "Skill cannot be empty.")
        mock_get.assert_not_called()

    @patch('scheduler.models.UserTable.objects.get')
    def test_add_skill_duplicate(self, mock_get):
        self.mock_ta.skills = "Python"
        mock_get.return_value = self.mock_ta

        success, message = AdminAssignmentPage.add_skill_to_ta(self.ta_id, "Python")

        self.assertFalse(success)
        self.assertEqual(message, "This skill is already assigned to the TA.")
        self.mock_ta.save.assert_not_called()

    @patch('scheduler.models.UserTable.objects.get')
    def test_ta_not_found(self, mock_get):
        mock_get.side_effect = UserTable.DoesNotExist

        success, message = AdminAssignmentPage.add_skill_to_ta(self.ta_id, self.skill)

        self.assertFalse(success)
        self.assertEqual(message, "TA not found or not eligible.")

    @patch('scheduler.models.UserTable.objects.get')
    def test_unexpected_error(self, mock_get):
        mock_get.side_effect = Exception("Database error")

        success, message = AdminAssignmentPage.add_skill_to_ta(self.ta_id, self.skill)

        self.assertFalse(success)
        self.assertTrue("An unexpected error occurred" in message)
