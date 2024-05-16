from django.core.exceptions import ObjectDoesNotExist

from scheduler.models import CourseTable, SectionTable


class AdminSectionManagementPage:
    def __init__(self):
        pass

    @staticmethod
    def createSection(sectionName, courseId, time):
        # Create a new course section
        try:
            course = CourseTable.objects.filter(id=courseId).first()
            existingCourseSection = SectionTable.objects.filter(name=sectionName, courseId=course).exists()

            if existingCourseSection:
                raise ValueError("Section already exists")
            elif sectionName == "":
                raise ValueError("Invalid course name")
            SectionTable.objects.create(name=sectionName, courseId=course, time=time)
            return "Section created successfully"
        except ObjectDoesNotExist:
            return "Failed to create section"
