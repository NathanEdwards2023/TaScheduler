from django.core.exceptions import ObjectDoesNotExist

from scheduler.models import SectionTable, UserTable, UserSectionJoinTable


class InstructorCourseManagementPage:
    def __init__(self):
        pass

    @staticmethod
    def assignInsToSection(sectionId, userId):
        # Create a new course section
        try:
            section = SectionTable.objects.filter(id=sectionId).first()
            user = UserTable.objects.filter(id=userId).first()

            if section is None:
                raise ValueError("No such section exists")
            if user is None:
                raise ValueError("No such user exists")
            if user.userType != "instructor":
                raise ValueError("The user is not an instructor")
            existingInsSection = UserSectionJoinTable.objects.filter(sectionId=section, userId=user).exists()
            if existingInsSection:
                raise ValueError("Instructor already assigned to section")
            UserSectionJoinTable.objects.create(sectionId=section, userId=user)
            return "Instructor assigned to section"
        except ObjectDoesNotExist:
            return "Failed to assign instructor"
