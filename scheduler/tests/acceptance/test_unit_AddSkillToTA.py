import unittest

from django.test import TestCase

from adminAssignmentPage import AdminAssignmentPage
from scheduler.models import UserTable
from userManagement import UserManagementPage


class AddSkillToTATests(TestCase):
    def setUp(self):
        # Setup a TA in the database
        self.ta = UserTable.objects.create(
            firstName="John",
            lastName="Doe",
            email="johndoe@example.com",
            userType='ta',
            skills=""
        )

    def test_add_skill_successfully(self):
        # Test adding a new skill successfully
        ta_id = self.ta.id
        skill = "Python"
        success, message = UserManagementPage.add_skill_to_ta(ta_id, skill)
        self.assertTrue(success)
        self.assertEqual(message, "Skill successfully added.")

        # Verify the skill was added
        updated_ta = UserTable.objects.get(pk=ta_id)
        self.assertIn(skill, updated_ta.skills)

    def test_add_empty_skill(self):
        # Test adding an empty skill
        ta_id = self.ta.id
        skill = ""
        success, message = UserManagementPage.add_skill_to_ta(ta_id, skill)
        self.assertFalse(success)
        self.assertEqual(message, "Skill cannot be empty.")

    def test_add_duplicate_skill(self):
        # Add a skill first
        ta_id = self.ta.id
        skill = "Python"
        UserManagementPage.add_skill_to_ta(ta_id, skill)

        # Try adding the same skill again
        success, message = UserManagementPage.add_skill_to_ta(ta_id, skill)
        self.assertFalse(success)
        self.assertEqual(message, "This skill is already assigned to the TA.")

    def test_ta_not_found(self):
        # Try adding a skill to a non-existing TA
        non_existent_ta_id = self.ta.id + 999
        skill = "Python"
        success, message = UserManagementPage.add_skill_to_ta(non_existent_ta_id, skill)
        self.assertFalse(success)
        self.assertEqual(message, "TA not found or not eligible.")


if __name__ == '__main__':
    unittest.main()
