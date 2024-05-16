import unittest

from django.test import TestCase
from unittest.mock import patch, MagicMock

from adminAssignmentPage import AdminAssignmentPage
from adminCourseManagement import AdminCourseManagementPage
from scheduler.models import LabTable, UserTable, SectionTable, UserLabJoinTable, UserSectionJoinTable


class TestAssignTAToLab(TestCase):
    def setUp(self):
        self.admin_page = AdminCourseManagementPage()
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
    def test_assign_tatolab_success(self, mock_section_update_or_create, mock_lab_update_or_create, mock_section_get,
                                    mock_user_get, mock_lab_get):
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
